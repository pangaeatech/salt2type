import { isValue } from "./index";
import { formatString, startsWithString, padLeftString } from "./strings";

/** Formats the specified number using the format string. */
export function formatNumber(n: number, format?: string): string {
    if (!format || format == "i") {
        return n.toString();
    }

    return netFormatNumber(n, format);
}

export function round(n: number, d?: number, rounding?: boolean) {
    const m = Math.pow(10, d || 0);
    n *= m;
    const sign: number = (n > 0 ? 1 : 0) | -(n < 0 ? 1 : 0);

    if (n % 1 === 0.5 * sign) {
        var f = Math.floor(n);
        return (f + (rounding ? (sign > 0 ? 1 : 0) : (f % 2) * sign)) / m;
    }

    return Math.round(n) / m;
}

/** Replaces null with undefined. */
export function unbox<T>(a: T | null | undefined): T | undefined {
    return a !== null ? a : undefined;
}

/** A class for doing math on nullable values. */
export class Nullable$1 {
    static eq(a: unknown, b: unknown) {
        return !isValue(a) ? !isValue(b) : a === b;
    }

    static ne(a: unknown, b: unknown) {
        return !isValue(a) ? !isValue(b) : a !== b;
    }

    static gt(a?: Date | number, b?: Date | number): boolean {
        return a !== undefined && b != undefined && a > b;
    }

    static ge(a?: Date | number, b?: Date | number): boolean {
        return a !== undefined && b != undefined && a >= b;
    }

    static lt(a?: Date | number, b?: Date | number): boolean {
        return a !== undefined && b != undefined && a < b;
    }

    static le(a?: Date | number, b?: Date | number): boolean {
        return a !== undefined && b != undefined && a <= b;
    }

    static add(a?: number, b?: number): number | undefined {
        return a !== undefined && b != undefined ? a + b : undefined;
    }

    static sub(a?: number, b?: number): number | undefined {
        return a !== undefined && b != undefined ? a - b : undefined;
    }
}

/** Number Format constants. */
export const NumberFormatInfo = {
    invariantInfo: {
        naNSymbol: "NaN",
        negativeSign: "-",
        positiveSign: "+",
        negativeInfinitySymbol: "-Infinity",
        positiveInfinitySymbol: "Infinity",

        percentSymbol: "%",
        percentGroupSizes: [3],
        percentDecimalDigits: 2,
        percentDecimalSeparator: ".",
        percentGroupSeparator: ",",
        percentPositivePattern: 0,
        percentNegativePattern: 0,

        currencySymbol: "$",
        currencyGroupSizes: [3],
        currencyDecimalDigits: 2,
        currencyDecimalSeparator: ".",
        currencyGroupSeparator: ",",
        currencyNegativePattern: 0,
        currencyPositivePattern: 0,

        numberGroupSizes: [3],
        numberDecimalDigits: 2,
        numberDecimalSeparator: ".",
        numberGroupSeparator: ","
    }
};

/** Compare 2 numbers. */
export function compare(a: number, b: number): number {
    return a - b;
}

function _commaFormatNumber(num, groups, decimal, comma) {
    var decimalPart: number | undefined = undefined;
    var decimalIndex = num.indexOf(decimal);
    if (decimalIndex > 0) {
        decimalPart = num.substr(decimalIndex);
        num = num.substr(0, decimalIndex);
    }

    var negative = startsWithString(num, "-");
    if (negative) {
        num = num.substr(1);
    }

    var groupIndex = 0;
    var groupSize = groups[groupIndex];
    if (num.length < groupSize) {
        return (negative ? "-" : "") + (decimalPart ? num + decimalPart : num);
    }

    var index = num.length;
    var s = "";
    var done = false;
    while (!done) {
        var length = groupSize;
        var startIndex = index - length;
        if (startIndex < 0) {
            groupSize += startIndex;
            length += startIndex;
            startIndex = 0;
            done = true;
        }
        if (!length) {
            break;
        }

        var part = num.substr(startIndex, length);
        if (s.length) {
            s = part + comma + s;
        } else {
            s = part;
        }
        index -= length;

        if (groupIndex < groups.length - 1) {
            groupIndex++;
            groupSize = groups[groupIndex];
        }
    }

    if (negative) {
        s = "-" + s;
    }
    return decimalPart ? s + decimalPart : s;
}

export function netFormatNumber(num: number, format: string): string {
    var s = "";
    var precision = -1;

    if (format.length > 1) {
        precision = parseInt(format.substr(1), 10);
    }

    var fs = format.charAt(0);
    switch (fs) {
        case "d":
        case "D":
            s = Math.trunc(Math.abs(num)).toString();
            if (precision != -1) {
                s = padLeftString(s, precision, 0x30);
            }
            if (num < 0) {
                s = "-" + s;
            }
            break;
        case "x":
        case "X":
            s = Math.trunc(Math.abs(num)).toString(16);
            if (fs == "X") {
                s = s.toUpperCase();
            }
            if (precision != -1) {
                s = padLeftString(s, precision, 0x30);
            }
            break;
        case "e":
        case "E":
            if (precision == -1) {
                s = num.toExponential();
            } else {
                s = num.toExponential(precision);
            }
            if (fs == "E") {
                s = s.toUpperCase();
            }
            break;
        case "f":
        case "F":
        case "n":
        case "N":
            if (precision == -1) {
                precision = NumberFormatInfo.invariantInfo.numberDecimalDigits;
            }
            s = num.toFixed(precision).toString();
            if (precision && NumberFormatInfo.invariantInfo.numberDecimalSeparator != ".") {
                var index = s.indexOf(".");
                s = s.substr(0, index) + NumberFormatInfo.invariantInfo.numberDecimalSeparator + s.substr(index + 1);
            }
            if (fs == "n" || fs == "N") {
                s = _commaFormatNumber(
                    s,
                    NumberFormatInfo.invariantInfo.numberGroupSizes,
                    NumberFormatInfo.invariantInfo.numberDecimalSeparator,
                    NumberFormatInfo.invariantInfo.numberGroupSeparator
                );
            }
            break;
        case "c":
        case "C":
            s = formatString(
                "{0}{1}{2}",
                num < 0 ? "-" : "",
                NumberFormatInfo.invariantInfo.currencySymbol,
                netFormatNumber(Math.abs(num), "N")
            );
            break;
        case "p":
        case "P":
            s = formatString(
                "{0}{1}{2}",
                num < 0 ? "-" : "",
                netFormatNumber(Math.abs(num) * 100, "N"),
                NumberFormatInfo.invariantInfo.percentSymbol
            );
            break;
    }

    return s;
}
