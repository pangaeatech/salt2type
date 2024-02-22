import { isValue } from "./index";

/** Returns whether or not the specified string is null or empty. */
export function isNullOrEmptyString(val: string): boolean {
    return !val || !val.length;
}

const _formatRE = /\{\{|\}\}|\{[^}{]+\}/g;

/** Formats the specified string with the specified numbered parameters. */
export function formatString(format: string, ...values: string[]): string {
    return format.replace(_formatRE, function (m) {
        if (m === "{{" || m === "}}") {
            return m.charAt(0);
        }

        var index = parseInt(m.substr(1), 10);
        return values[index] || "";
    });
}

export function regexpEscape(s: string): string {
    return s.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");
}

export function netSplit(s: string, strings: string[], limit: number, options?: number): string[] {
    const re = new RegExp(strings.map(regexpEscape).join("|"), "g");
    const res: string[] = [];
    var m;

    for (let i = 0; ; i = re.lastIndex) {
        if ((m = re.exec(s))) {
            if (options !== 1 || m.index > i) {
                if (res.length === limit - 1) {
                    res.push(s.substr(i));
                    return res;
                } else {
                    res.push(s.substring(i, m.index));
                }
            }
        } else {
            if (options !== 1 || i !== s.length) {
                res.push(s.substr(i));
            }
            return res;
        }
    }
}

export function compareStrings(s1: string, s2: string, ignoreCase?: boolean) {
    if (!isValue(s1)) {
        return isValue(s2) ? -1 : 0;
    }

    if (!isValue(s2)) {
        return 1;
    }

    if (ignoreCase) {
        if (s1) {
            s1 = s1.toUpperCase();
        }
        if (s2) {
            s2 = s2.toUpperCase();
        }
    }

    s1 = s1 || "";
    s2 = s2 || "";

    if (s1 == s2) {
        return 0;
    }

    if (s1 < s2) {
        return -1;
    }

    return 1;
}

/** Returns whether or not the specified string starts with the given prefix. */
export function startsWithString(value: string, prefix: string): boolean {
    return value.startsWith(prefix);
}

/** Returns whether or not the specified string ends with the given suffix. */
export function endsWithString(value: string, suffix: string): boolean {
    return value.endsWith(suffix);
}

export function stringFromChar(ch: string, count: number): string {
    var s = ch;
    for (var i = 1; i < count; i++) {
        s += ch;
    }
    return s;
}

export function htmlDecode(s: string): string {
    return s.replace(/&([^;]+);/g, function (_, e) {
        if (e[0] === "#") return String.fromCharCode(parseInt(e.substr(1), 10));
        switch (e) {
            case "quot":
                return '"';
            case "apos":
                return "'";
            case "amp":
                return "&";
            case "lt":
                return "<";
            case "gt":
                return ">";
            default:
                return "&" + e + ";";
        }
    });
}

export function htmlEncode(s: string): string {
    return s
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

export function jsEncode(s: string, q?: boolean) {
    s = s.replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/"/g, '\\"');
    return q ? '"' + s + '"' : s;
}

export function padLeftString(s: string, totalWidth: number, ch?: number): string {
    if (s.length < totalWidth) {
        return stringFromChar(String.fromCharCode(ch || 0x20), totalWidth - s.length) + s;
    }

    return s;
}

export function padRightString(s: string, totalWidth: number, ch?: number): string {
    if (s.length < totalWidth) {
        return s + stringFromChar(String.fromCharCode(ch || 0x20), totalWidth - s.length);
    }

    return s;
}

export function replaceAllString(s: string, oldValue: string, newValue: string): string {
    newValue = newValue || "";
    return s.split(oldValue).join(newValue);
}

export function parseXml(markup: string) {
    try {
        return new DOMParser().parseFromString(markup, "text/xml");
    } catch (ex) {}

    return undefined;
}

export function isLower(c: number): boolean {
    const s = String.fromCharCode(c);
    return s === s.toLowerCase() && s !== s.toUpperCase();
}

export function isUpper(c: number): boolean {
    const s = String.fromCharCode(c);
    return s !== s.toLowerCase() && s === s.toUpperCase();
}
