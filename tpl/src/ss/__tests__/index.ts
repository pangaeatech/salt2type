import {
    EventArgs,
    isNullOrUndefined,
    coalesce,
    isValue,
    referenceEquals,
    staticEquals,
    shallowCopy,
    Type,
    cast,
    safeCast,
    getDefaultValue,
    createInstance
} from "../index";

describe("EventArgs class", () => {
    describe("Empty", () => {
        it("should create an instance of EventArgs", () => {
            expect(EventArgs.Empty instanceof EventArgs).toBe(true);
        });

        it("should return the same instance every time", () => {
            expect(EventArgs.Empty).toBe(EventArgs.Empty);
        });
    });
});

describe("isNullOrUndefined function", () => {
    test("it correctly identifies a null value", () => {
        const val = null;
        expect(isNullOrUndefined(val)).toBeTruthy();
    });

    test("it correctly identifies an undefined value", () => {
        const val = undefined;
        expect(isNullOrUndefined(val)).toBeTruthy();
    });

    test("it correctly identifies a non-null value", () => {
        const val = "example";
        expect(isNullOrUndefined(val)).toBeFalsy();
    });
});

describe("coalesce function", () => {
    test("it returns the first non-null/non-undefined value in the arguments list", () => {
        const val1 = null;
        const val2 = undefined;
        const val3 = "example";
        expect(coalesce(val1, val2, val3)).toBe(val3);
    });

    test("it returns undefined when all arguments are null/undefined", () => {
        const val1 = null;
        const val2 = undefined;
        expect(coalesce(val1, val2)).toBeUndefined();
    });
});

describe("isValue function", () => {
    test("it correctly identifies a null value", () => {
        const val = null;
        expect(isValue(val)).toBeFalsy();
    });

    test("it correctly identifies an undefined value", () => {
        const val = undefined;
        expect(isValue(val)).toBeFalsy();
    });

    test("it correctly identifies a non-null/undefined value", () => {
        const val = "example";
        expect(isValue(val)).toBeTruthy();
    });
});

describe("referenceEquals function", () => {
    test("it returns true for two identical non-null/non-undefined values", () => {
        const val1 = "example";
        const val2 = "example";
        expect(referenceEquals(val1, val2)).toBeTruthy();
    });

    test("it returns false for two different non-null/non-undefined values", () => {
        const val1 = "example1";
        const val2 = "example2";
        expect(referenceEquals(val1, val2)).toBeFalsy();
    });

    test("it returns true for two null values", () => {
        const val1 = null;
        const val2 = null;
        expect(referenceEquals(val1, val2)).toBeTruthy();
    });

    test("it returns true for two undefined values", () => {
        const val1 = undefined;
        const val2 = undefined;
        expect(referenceEquals(val1, val2)).toBeTruthy();
    });

    test("it returns true for a null/undefined value and an identical value", () => {
        const val1 = null;
        const val2 = "example";
        expect(referenceEquals(val1, val1)).toBeTruthy();
    });

    test("it returns false for a null/undefined value and a different value", () => {
        const val1 = null;
        const val2 = "example";
        expect(referenceEquals(val1, val2)).toBeFalsy();
    });
});

describe("staticEquals function", () => {
    test("it returns true for two identical non-null/non-undefined values", () => {
        const val1 = "example";
        const val2 = "example";
        expect(staticEquals(val1, val2)).toBeTruthy();
    });

    test("it returns false for two different non-null/non-undefined values", () => {
        const val1 = "example1";
        const val2 = "example2";
        expect(staticEquals(val1, val2)).toBeFalsy();
    });

    test("it returns true for two null values", () => {
        const val1 = null;
        const val2 = null;
        expect(staticEquals(val1, val2)).toBeTruthy();
    });

    test("it returns true for two undefined values", () => {
        const val1 = undefined;
        const val2 = undefined;
        expect(staticEquals(val1, val2)).toBeTruthy();
    });

    test("it returns true for a null/undefined value and an identical value", () => {
        const val1 = null;
        const val2 = "example";
        expect(staticEquals(val1, val1)).toBeTruthy();
    });

    test("it returns false for a null/undefined value and a different value", () => {
        const val1 = null;
        const val2 = "example";
        expect(staticEquals(val1, val2)).toBeFalsy();
    });
});

describe("shallowCopy function", () => {
    test("shallowCopy should copy values of source onto target", () => {
        const source = { a: 1, b: "hello", c: { d: true } };
        const target = {};

        shallowCopy(source, target);

        expect(target).toEqual(source);
    });

    test("shallowCopy should not modify target if source is empty", () => {
        const source = {};
        const target = { a: 1, b: "hello", c: { d: true } };

        shallowCopy(source, target);

        expect(target).toEqual({ a: 1, b: "hello", c: { d: true } });
    });

    test("shallowCopy should overwrite existing properties in target", () => {
        const source = { a: 2, b: "world" };
        const target = { a: 1, b: "hello" };

        shallowCopy(source, target);

        expect(target).toEqual({ a: 2, b: "world" });
    });

    test("shallowCopy should not copy properties from prototype of source", () => {
        const source = Object.create({ a: 1 });
        source.b = 2;

        const target = {};

        shallowCopy(source, target);

        expect(target).toEqual({ b: 2 });
    });
});

describe("Cast/safeCast functions", () => {
    class MyClass {
        name: string;
        constructor() {
            this.name = "MyClass";
        }
    }

    test("cast should return the same value", () => {
        const obj = new MyClass();
        const castedObj = cast(obj, MyClass);
        expect(castedObj).toBe(obj);
    });

    test("safeCast should return the same value", () => {
        const obj = new MyClass();
        const castedObj = safeCast(obj, MyClass);
        expect(castedObj).toBe(obj);
    });

    test("Type.createInstance should create an instance of the given type", () => {
        class SubClass extends MyClass {
            age = 5;
        }
        const SubClassType: Type<SubClass> = SubClass;
        const instance = new SubClassType();
        expect(instance instanceof SubClass).toBe(true);
    });
});

describe("getDefaultValue function", () => {
    test("getDefaultValue returns false for Boolean type", () => {
        expect(getDefaultValue(Boolean)).toBe(false);
    });

    test("getDefaultValue returns Date with timestamp 0 for Date type", () => {
        expect(getDefaultValue(Date)).toEqual(new Date(0));
    });

    test("getDefaultValue returns 0 for Number type", () => {
        expect(getDefaultValue(Number)).toBe(0);
    });

    test("getDefaultValue returns undefined for unknown type", () => {
        expect(getDefaultValue(String)).toBeUndefined();
    });
});

describe("createInstance function", () => {
    test("createInstance returns new instance of Boolean type if createInstance method not present", () => {
        expect(createInstance(Boolean)).toEqual(false);
    });

    test("createInstance returns instance created using createInstance method", () => {
        class Typ {
            val: string;
            constructor(val?: string) {
                this.val = val ?? "garb";
            }

            static createInstance() {
                return new Typ("food");
            }
        }

        expect(createInstance(Typ).val).toEqual("food");
    });

    test("createInstance returns default instance without createInstance method", () => {
        class Typ {
            val: string;
            constructor(val?: string) {
                this.val = val ?? "garb";
            }
        }

        expect(createInstance(Typ).val).toEqual("garb");
    });

    test("createInstance returns new instance of Date type if createInstance method is null", () => {
        expect(createInstance(Date)).toEqual(new Date(0));
    });

    test("createInstance returns new instance of Number type if createInstance method not present", () => {
        expect(createInstance(Number)).toEqual(0);
    });

    test("createInstance returns new instance of String type if createInstance method not present", () => {
        expect(createInstance(String)).toEqual("");
    });
});
