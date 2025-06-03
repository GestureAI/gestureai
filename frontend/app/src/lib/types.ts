// For WS communication and ui state
export interface ChatMessageFromServer {
	id: string; // Server generated ID.
	type: 'message';
	username: string;
	message: string;
	timestamp: number;
}

// For messages added to the ui immediately by the sender, pending server confirmation.
export interface PendingChatMessage {
	id: `client-${string}`; // Temporary client-side ID, e.g., "client-uuid".
	type: 'message';
	username: string;
	message: string;
	timestamp: number;
}

export type DisplayMessage = ChatMessageFromServer | PendingChatMessage;

export interface HistoryMessage {
	type: 'history';
	messages: ChatMessageFromServer[]; // History only contains server-confirmed messages
}

export type WebSocketIncomingData = HistoryMessage | ChatMessageFromServer;

export interface User {
	username: string;
}

export type UploadedFile = {
	name: string;
	size: number;
	key: string;
	lastModified?: number;
	serverData: null | Record<string, unknown>;
	url: string;
	appUrl: string;
	ufsUrl: string;
	customId: null | string;
	type: string;
	fileHash: string;
};
