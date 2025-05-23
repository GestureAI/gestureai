export class UseAutoScroll {
	#ref = $state<HTMLElement>();
	#scrollY: number = $state(0);
	#userHasScrolled = $state(false);
	private lastScrollHeight = 0;

	// This sets everything up once #ref is bound
	set ref(ref: HTMLElement | undefined) {
		this.#ref = ref;

		if (!this.#ref) return;

		this.lastScrollHeight = this.#ref.scrollHeight;

		// start from bottom or start position
		this.#ref.scrollTo(0, this.#scrollY ? this.#scrollY : this.#ref.scrollHeight);

		this.#ref.addEventListener('scroll', () => {
			if (!this.#ref) return;

			this.#scrollY = this.#ref.scrollTop;

			this.disableAutoScroll();
		});

		window.addEventListener('resize', () => {
			this.scrollToBottom(true);
		});

		// should detect when something changed that effected the scroll height
		const observer = new MutationObserver(() => {
			if (!this.#ref) return;

			if (this.#ref.scrollHeight !== this.lastScrollHeight) {
				this.scrollToBottom(true);
			}

			this.lastScrollHeight = this.#ref.scrollHeight;
		});

		observer.observe(this.#ref, { childList: true, subtree: true });
	}

	get ref() {
		return this.#ref;
	}

	get scrollY() {
		return this.#scrollY;
	}

	/** Checks if the container is scrolled to the bottom */
	get isAtBottom() {
		if (!this.#ref) return true;

		return this.#scrollY + this.#ref.offsetHeight >= this.#ref.scrollHeight;
	}

	/** Disables auto scrolling until the container is scrolled back to the bottom */
	disableAutoScroll() {
		if (this.isAtBottom) {
			this.#userHasScrolled = false;
		} else {
			this.#userHasScrolled = true;
		}
	}

	/** Scrolls the container to the bottom */
	scrollToBottom(auto = false) {
		if (!this.#ref) return;

		// don't auto scroll if user has scrolled
		if (auto && this.#userHasScrolled) return;

		this.#ref.scrollTo(0, this.#ref.scrollHeight);
	}
}
