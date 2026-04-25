export type FieldErrors = Record<string, string | string[]>;

export class ApiError extends Error {
	status: number;
	fieldErrors: FieldErrors;

	constructor(message: string, status = 0, fieldErrors: FieldErrors = {}) {
		super(message);
		this.name = 'ApiError';
		this.status = status;
		this.fieldErrors = fieldErrors;
	}
}

export interface User {
	id: number;
	email: string;
	username?: string;
	first_name?: string;
	last_name?: string;
	avatar?: string | null;
	is_verified?: boolean;
	is_staff?: boolean;
}

export interface AuthTokens {
	access: string;
	refresh: string;
}
