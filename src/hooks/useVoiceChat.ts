import { useCallback, useEffect, useRef, useState } from 'react';
import type { Character } from '@/data/characters';
import { useAudioWorklet } from './useAudioWorklet';
import { useVoiceSocket, type VoiceState } from './useVoiceSocket';

export type TurnState = 'idle' | 'listening' | 'processing' | 'speaking' | 'error';

export interface ChatMessage {
  role: 'user' | 'assistant';
  text: string;
}

export interface UseVoiceChatReturn {
  turnState: TurnState;
  lastTranscript: string;
  lastResponse: string;
  errorMessage: string;
  messages: ChatMessage[];
  isConnected: boolean;
  isConnecting: boolean;
  isRecording: boolean;
  isPlaying: boolean;
  micLevel: number;
  toggleRecording: () => void;
  reset: () => void;
  sendText: (text: string) => Promise<void>;
}

const VOICE_SERVER_URL =
  import.meta.env.VITE_VOICE_SERVER_URL ||
  (typeof window !== 'undefined' && window.location.protocol === 'https:'
    ? `wss://${window.location.host}`
    : `ws://${window.location.host}`);

const VOICE_SERVER_TOKEN = import.meta.env.VITE_VOICE_SERVER_API_KEY;

function log(...args: unknown[]) {
  console.log('[VoiceChat]', ...args);
}

export function useVoiceChat(character: Character | null): UseVoiceChatReturn {
  const [turnState, setTurnState] = useState<VoiceState>('idle');
  const [lastTranscript, setLastTranscript] = useState('');
  const [lastResponse, setLastResponse] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const characterRef = useRef(character);
  const turnStateRef = useRef(turnState);

  useEffect(() => {
    characterRef.current = character;
  }, [character]);

  useEffect(() => {
    turnStateRef.current = turnState;
  }, [turnState]);

  const handleStateChange = useCallback((state: VoiceState) => {
    log('state', state);
    setTurnState(state);
    if (state === 'processing' || state === 'speaking') {
      audio.stopRecording();
    }
  }, []);

  const handleTranscript = useCallback((text: string, isFinal: boolean) => {
    if (!isFinal) return;
    setLastTranscript(text);
    setMessages((prev) => [...prev, { role: 'user', text }]);
  }, []);

  const handleAssistantText = useCallback((text: string) => {
    setLastResponse((prev) => prev + text);
    setMessages((prev) => {
      if (prev.length > 0 && prev[prev.length - 1].role === 'assistant') {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        updated[updated.length - 1] = { ...last, text: last.text + text };
        return updated;
      }
      return [...prev, { role: 'assistant', text }];
    });
  }, []);

  const handleError = useCallback((code: string, message: string) => {
    log('server error', code, message);
    setErrorMessage(`${code}: ${message}`);
  }, []);

  const audio = useAudioWorklet({
    onPcmFrame: useCallback((pcm: ArrayBuffer) => {
      socket.sendBinary(pcm);
    }, []),
    onError: useCallback((msg: string) => {
      setErrorMessage(msg);
    }, []),
  });

  const socket = useVoiceSocket({
    url: VOICE_SERVER_URL,
    token: VOICE_SERVER_TOKEN,
    sessionId: 'mobile',
    deviceType: 'audio',
    onStateChange: handleStateChange,
    onTranscript: handleTranscript,
    onAssistantText: handleAssistantText,
    onError: handleError,
    onBinary: useCallback((pcm: ArrayBuffer) => {
      audio.playPcm(pcm);
    }, [audio]),
    reconnect: true,
  });

  // Send character/mode config when connected.
  useEffect(() => {
    if (!socket.connected || !character) return;
    socket.sendConfigChange({ character: character.id, mode: 'default' });
  }, [socket.connected, character, socket.sendConfigChange]);

  const toggleRecording = useCallback(() => {
    const state = turnStateRef.current;
    setErrorMessage('');

    if (state === 'listening' || state === 'wake_detected') {
      audio.stopRecording();
      return;
    }

    if (state === 'speaking') {
      socket.sendCommand('interrupt');
      audio.stopPlayback();
      return;
    }

    setLastTranscript('');
    setLastResponse('');

    socket.sendCommand('wake');
    void audio.unlockAudio().then(() => audio.startRecording());
  }, [audio, socket]);

  const reset = useCallback(() => {
    socket.sendCommand('reset');
    audio.stopRecording();
    audio.stopPlayback();
    setTurnState('idle');
    setLastTranscript('');
    setLastResponse('');
    setErrorMessage('');
    setMessages([]);
  }, [socket, audio]);

  const sendText = useCallback(
    async (text: string) => {
      if (!text.trim()) return;
      await audio.unlockAudio();

      setMessages((prev) => [...prev, { role: 'user', text: text.trim() }]);
      setLastResponse('');
      setErrorMessage('');

      if (socket.connected) {
        socket.sendTextInput(text.trim());
      } else {
        setErrorMessage('Not connected to voice server.');
      }
    },
    [socket, audio]
  );

  return {
    turnState: turnState === 'wake_detected' || turnState === 'interrupted' ? 'idle' : turnState,
    lastTranscript,
    lastResponse,
    errorMessage,
    messages,
    isConnected: socket.connected,
    isConnecting: socket.connecting,
    isRecording: audio.isRecording,
    isPlaying: audio.isPlaying,
    micLevel: audio.micLevel,
    toggleRecording,
    reset,
    sendText,
  };
}
