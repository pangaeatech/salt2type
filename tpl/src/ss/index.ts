import { v4 as newGuid } from "uuid";

export type Func<T1, T2> = (a: T1) => T2;
export type TypeOption<T1, T2, T3 = void, T4 = void> = T1 | T2 | T3 | T4;

export { default as StringBuilder } from "./StringBuilder";
export { default as Stopwatch } from "./Stopwatch";
export { default as TimeSpan } from "./TimeSpan";
export { default as Enum } from "./Enum";

export { utcNow, toUTC, fromUTC, today, formatDate, netFormatDate } from "./dates";
export { formatNumber, round, unbox, Nullable$1, NumberFormatInfo, compare, netFormatNumber } from "./numbers";
export {
    Action,
    Delegate,
    mkdel,
    delegateCombine,
    delegateRemove,
    delegateEquals,
    delegateClone,
    thisFix,
    getInvocationList
} from "./delegates";
export {
    Exception,
    AggregateException,
    AmbiguousMatchException,
    ArgumentException,
    ArgumentNullException,
    ArgumentOutOfRangeException,
    DivideByZeroException,
    FormatException,
    InvalidCastException,
    InvalidOperationException,
    JsErrorException,
    KeyNotFoundException,
    NotImplementedException,
    NotSupportedException,
    NullReferenceException,
    PromiseException
} from "./exceptions";
export {
    isNullOrEmptyString,
    formatString,
    regexpEscape,
    netSplit,
    compareStrings,
    startsWithString,
    endsWithString,
    stringFromChar,
    htmlDecode,
    htmlEncode,
    jsEncode,
    padLeftString,
    padRightString,
    replaceAllString,
    parseXml,
    isLower,
    isUpper
} from "./strings";
export {
    Dictionary,
    IDisposable,
    IEnumerator,
    IEnumerable,
    ArrayEnumerator,
    ObjectEnumerator,
    IteratorBlockEnumerable,
    IteratorBlockEnumerator,
    insert,
    add,
    remove,
    indexOf,
    getItem,
    setItem,
    removeAt,
    indexOfArray,
    contains,
    arrayLength,
    arrayPeekFront,
    arrayPeekBack,
    arrayRemoveRange,
    arrayAddRange,
    arrayExtract,
    arrayFromEnumerable,
    arrayClone,
    clear,
    count,
    getEnumerator,
    getKeyCount,
    clearKeys,
    keyExists,
    mkdict,
    repeat,
    arrayFill,
    arrayCopy,
    arrayInsertRange
} from "./collections";

/** An empty class for holding event arguments. */
export class EventArgs {
    static Empty = new EventArgs();
}

export class CancelEventArgs extends EventArgs {
    cancel = false;
}

/** Returns whether or not the specified item is null or undefined. */
export function isNullOrUndefined(item: unknown): boolean {
    return item === null || item === undefined;
}

/** Returns the first item that is not null or undefined. */
export function coalesce<T>(...items: (T | null | undefined)[]): T | undefined {
    for (const item of items) {
        if (item !== undefined && item !== null) {
            return item;
        }
    }

    return undefined;
}

/** Returns whether or not the specified item is not null nor undefined. */
export function isValue(item: unknown): boolean {
    return item !== null && item !== undefined;
}

/** Returns whether or not the specified items are reference equal. */
export function referenceEquals(a: unknown, b: unknown): boolean {
    return a === b || (!isValue(a) && !isValue(b));
}

/** Returns whether or not the specified items are reference equal. */
export function staticEquals(a: unknown, b: unknown): boolean {
    return referenceEquals(a, b);
}

/** Guid */
export const Guid = { newGuid };

/** Perform a shallow copy of an object. */
export function shallowCopy(source: unknown, target: any): void {
    Object.assign(target, source);
}

export interface Type<T> {
    new (): T;

    createInstance?: () => T;

    __typeName?: string;
    name?: string;
    toString: () => string;
}

export function cast<F extends T, T>(o: F, typ: Type<T>): T {
    return o as unknown as T;
}

export function safeCast<F extends T, T>(o: F, typ: Type<T>): T {
    return o as unknown as T;
}

export function isInstanceOfType<T1, T2>(instance: T1 | null | undefined, typ: Type<T2>): boolean {
    if (instance === null || instance === undefined) {
        return false;
    }

    return isAssignableFrom(typ, instance.constructor as Type<T1>);
}

export function isAssignableFrom<T1, T2>(target: Type<T1>, typ: Type<T2>): boolean {
    return referenceEquals(target, typ) || typ.prototype instanceof target;
}

export function getDefaultValue<T>(typ: Type<T>): T | undefined {
    if (referenceEquals(typ, Boolean)) {
        return false as unknown as T;
    }

    if (referenceEquals(typ, Date)) {
        return new Date(0) as unknown as T;
    }

    if (referenceEquals(typ, Number)) {
        return 0 as unknown as T;
    }

    return undefined;
}

export function createInstance<T>(typ: Type<T>): T {
    if (typeof typ.createInstance === "function") {
        return typ.createInstance();
    }

    if (referenceEquals(typ, Boolean)) {
        return false as unknown as T;
    }

    if (referenceEquals(typ, Date)) {
        return new Date(0) as unknown as T;
    }

    if (referenceEquals(typ, Number)) {
        return 0 as unknown as T;
    }

    if (referenceEquals(typ, String)) {
        return "" as unknown as T;
    }

    return new typ();
}

export function getInstanceType<T>(instance?: T | null): Type<T> {
    if (!instance) {
        throw "Cannot get type of null";
    }

    try {
        return instance.constructor as unknown as Type<T>;
    } catch (ex) {
        return Object as unknown as Type<T>;
    }
}

export function getTypeFullName<T>(typ: Type<T>): string {
    return typ.__typeName || typ.name || (typ.toString().match(/^\s*function\s*([^\s(]+)/) || [])[1] || "Object";
}

export function getTypeName<T>(typ: Type<T>): string {
    var fullName = getTypeFullName(typ);
    var bIndex = fullName.indexOf("[");
    var nsIndex = fullName.lastIndexOf(".", bIndex >= 0 ? bIndex : fullName.length);
    return nsIndex > 0 ? fullName.substr(nsIndex + 1) : fullName;
}

export function getTypeNamespace<T>(typ: Type<T>): string {
    var fullName = getTypeFullName(typ);
    var bIndex = fullName.indexOf("[");
    var nsIndex = fullName.lastIndexOf(".", bIndex >= 0 ? bIndex : fullName.length);
    return nsIndex > 0 ? fullName.substr(0, nsIndex) : "";
}
