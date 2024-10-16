export interface Stringable {
    toString: () => string;
}

export default class StringBuilder {
    private _parts: string[];

    constructor(s?: string | null) {
        if (s && s.length > 0) {
            this._parts = [s];
        } else {
            this._parts = [];
        }
    }

    append(o: Stringable | null | undefined): StringBuilder {
        if (o !== null && o != undefined) {
            this._parts.push(o.toString());
        }

        return this;
    }

    appendChar(c: number): StringBuilder {
        return this.append(String.fromCharCode(c));
    }

    appendLine(s: string | undefined | null): StringBuilder {
        this.append(s || "");
        this.append("\r\n");
        return this;
    }

    appendLineChar(c: number): StringBuilder {
        return this.appendLine(String.fromCharCode(c));
    }

    clear() {
        this._parts = [];
    }

    toString() {
        return this._parts.join("");
    }
}
