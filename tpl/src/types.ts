export type JsDictionary = Record<string, any>;

export type Action<T> = () => T;

export type Delegate = Action<void>;

export type Func<T1, T2> = (a: T1) => T2;

export type TypeOption<T1, T2, T3 = void, T4 = void> = T1 | T2 | T3 | T4;
