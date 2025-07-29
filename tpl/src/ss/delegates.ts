export interface Action {
    (): void;
}

export interface Delegate extends Action {
    (): void;

    _targets: Action[];
}

function _mkdel(targets: Action[]): Delegate {
    const del = function () {
        for (const action of (arguments.callee as Delegate)._targets) {
            action();
        }
    };

    del._targets = targets;

    return del;
}

export function mkdel<T>(obj: T | undefined | null, method: (o?: T) => void): Delegate {
    if (obj !== null && obj !== undefined) {
        return _mkdel([
            () => {
                method(obj);
            }
        ]);
    }

    return _mkdel([method]);
}

export function delegateCombine(d1: Delegate, d2: Delegate): Delegate {
    return _mkdel([...d1._targets, ...d2._targets]);
}

function _contains(targets: Action[], item: Action): boolean {
    for (const target of targets) {
        if (target === item) {
            return true;
        }
    }

    return false;
}

export function delegateRemove(d1: Delegate, d2: Delegate): Delegate {
    const targets: Action[] = [];
    for (const d of d1._targets) {
        if (!_contains(d2._targets, d)) {
            targets.push(d);
        }
    }

    return _mkdel(targets);
}

export function delegateEquals(a: Delegate, b: Delegate): boolean {
    if (a === b) {
        return true;
    }

    if (!a._targets && !b._targets) {
        return false;
    }

    const ta = a._targets;
    const tb = b._targets;

    if (ta.length != tb.length) {
        return false;
    }

    for (var i = 0; i < ta.length; i++) {
        if (ta[i] !== tb[i]) {
            return false;
        }
    }

    return true;
}

export function delegateClone(source: Delegate): Delegate {
    return _mkdel([...source._targets]);
}

export function thisFix<T extends Function>(source: T): T {
    return function () {
        var x: any[] = [null];
        for (var i = 0; i < arguments.length; i++) x.push(arguments[i]);
        return source.apply(source, x);
    } as unknown as T;
}

export function getInvocationList(delegate: Delegate): Action[] {
    return delegate._targets;
}
