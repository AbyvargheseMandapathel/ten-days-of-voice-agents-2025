'use client';

import { useEffect, useState } from 'react';
import { useRoomContext } from '@livekit/components-react';
import { RoomEvent, DataPacket_Kind, RemoteParticipant } from 'livekit-client';

export function Receipt() {
  const room = useRoomContext();
  const [receiptHtml, setReceiptHtml] = useState<string | null>(null);

  useEffect(() => {
    const handleData = (
      payload: Uint8Array,
      participant: RemoteParticipant | undefined,
      kind?: DataPacket_Kind,
      topic?: string
    ) => {
      if (topic === 'receipt') {
        try {
          const decoder = new TextDecoder();
          const html = decoder.decode(payload);
          console.log('Receipt received:', html.substring(0, 50) + '...');
          setReceiptHtml(html);
        } catch (error) {
          console.error('Failed to decode receipt data:', error);
        }
      }
    };

    room.on(RoomEvent.DataReceived, handleData);

    return () => {
      room.off(RoomEvent.DataReceived, handleData);
    };
  }, [room]);

  if (!receiptHtml) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="relative max-w-md w-full coffee-card p-6">
        <button
          onClick={() => setReceiptHtml(null)}
          className="absolute top-2 right-2 text-coffee-text hover:text-coffee-accent font-bold"
        >
          ✕
        </button>
        <div
          dangerouslySetInnerHTML={{ __html: receiptHtml }}
          className="animate-in fade-in zoom-in duration-300"
        />
      </div>
    </div>
  );
}
