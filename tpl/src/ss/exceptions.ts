import { Stringable } from "./StringBuilder";

export class Exception {
    private _message: string;
    private _innerException: Exception | null;
    private _error: Error;

    constructor(message?: string | null, innerException?: Exception, cause?: Error) {
        this._message = message || "An error occurred.";
        this._innerException = innerException ?? null;
        this._error = cause ?? new Error();
    }

    get_message(): string {
        return this._message;
    }

    get_innerException(): Exception | null {
        return this._innerException;
    }

    get_stack() {
        return this._error.stack;
    }

    static wrap(o: Exception | Error | Stringable) {
        if (o instanceof Exception) {
            return o;
        } else if (o instanceof TypeError) {
            // TypeError can either be 'cannot read property blah of null/undefined' (proper NullReferenceException), or it can be eg. accessing a non-existent method of an object.
            // As long as all code is compiled, they should with a very high probability indicate the use of a null reference.
            return new NullReferenceException(o.message, new JsErrorException(o));
        } else if (o instanceof RangeError) {
            return new ArgumentOutOfRangeException("", o.message, new JsErrorException(o));
        } else if (o instanceof Error) {
            return new JsErrorException(o);
        } else {
            return new Exception(o.toString());
        }
    }
}

export class AggregateException extends Exception {
    innerExceptions: Exception[];

    constructor(message: string | undefined | null, innerExceptions: Exception[]) {
        super(message || "One or more errors occurred.", innerExceptions[0]);
        this.innerExceptions = innerExceptions;
    }

    flatten(): AggregateException {
        var inner: Exception[] = [];
        for (const ex of this.innerExceptions) {
            if (ex instanceof AggregateException) {
                inner.push(...ex.innerExceptions);
            } else {
                inner.push(ex);
            }
        }

        return new AggregateException(this.get_message(), inner);
    }
}

export class AmbiguousMatchException extends Exception {
    constructor(message?: string | null, innerException?: Exception) {
        super(message || "Ambiguous match.", innerException);
    }
}

export class ArgumentException extends Exception {
    paramName: string;

    constructor(message?: string | null, paramName?: string | null, innerException?: Exception) {
        super(message || "Value does not fall within the expected range.", innerException);
        this.paramName = paramName || "";
    }
}

export class ArgumentNullException extends ArgumentException {
    constructor(paramName?: string | null, message?: string | null, innerException?: Exception) {
        const suffix = paramName ? `\nParameter name: ${paramName}` : "";
        super((message || "Value cannot be null.") + suffix, paramName, innerException);
    }
}

export class ArgumentOutOfRangeException extends ArgumentException {
    actualValue?: unknown;

    constructor(paramName?: string | null, message?: string | null, innerException?: Exception, actualValue?: unknown) {
        const suffix = paramName ? `\nParameter name: ${paramName}` : "";
        super((message || "Value is out of range.") + suffix, paramName, innerException);
        this.actualValue = actualValue;
    }
}

export class DivideByZeroException extends Exception {
    constructor(message?: string | null, innerException?: Exception) {
        super(message || "Division by 0.", innerException);
    }
}

export class FormatException extends Exception {
    constructor(message?: string | null, innerException?: Exception) {
        super(message || "Invalid format.", innerException);
    }
}

export class InvalidCastException extends Exception {
    constructor(message?: string | null, innerException?: Exception) {
        super(message || "The cast is not valid.", innerException);
    }
}

export class InvalidOperationException extends Exception {
    constructor(message?: string | null, innerException?: Exception) {
        super(message || "Operation is not valid due to the current state of the object.", innerException);
    }
}

export class JsErrorException extends Exception {
    constructor(error: Error, message?: string | null, innerException?: Exception) {
        super(message || error.message, innerException, error);
    }
}

export class KeyNotFoundException extends Exception {
    constructor(message?: string | null, innerException?: Exception) {
        super(message || "Key not found.", innerException);
    }
}

export class NotImplementedException extends Exception {
    constructor(message?: string | null, innerException?: Exception) {
        super(message || "The method or operation is not implemented.", innerException);
    }
}

export class NotSupportedException extends Exception {
    constructor(message?: string | null, innerException?: Exception) {
        super(message || "Specified method is not supported.", innerException);
    }
}

export class NullReferenceException extends Exception {
    constructor(message?: string | null, innerException?: Exception, cause?: Error) {
        super(message || "Object is null.", innerException);
    }
}

export class PromiseException extends Exception {
    private _args: Array<string | undefined | null>;

    constructor(args: Array<string | undefined | null>, message?: string | null, innerException?: Exception) {
        super(message || args[0] || "Object is null.", innerException);
        this._args = [...args];
    }

    get_arguments() {
        return this._args;
    }
}
