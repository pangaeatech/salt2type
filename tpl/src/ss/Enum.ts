import { ArgumentException } from "./exceptions";

interface EnumObject {
    [key: string | number]: string | number;
}

export default class Enum {
    static parse(item: EnumObject, s: string): number {
        const val = item[s];
        if (val === undefined) {
            throw new ArgumentException("Invalid Enumeration Value");
        }

        return val as number;
    }

    static toString(item: EnumObject, value: number): string {
        const val = item[value];
        if (val === undefined) {
            throw new ArgumentException("Invalid Enumeration Value");
        }

        return val as string;
    }

    static getValues(item: EnumObject): number[] {
        return Object.keys(item)
            .map((i) => Number(i))
            .filter((i) => !isNaN(i));
    }
}
