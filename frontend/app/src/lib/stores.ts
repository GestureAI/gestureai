import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';

export const usernameStore: Writable<string> = writable('');
