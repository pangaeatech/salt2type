import StringBuilder from "./StringBuilder";

/** Returns the current UTC date. */
export function utcNow(): Date {
    var d = new Date();
    return new Date(
        d.getUTCFullYear(),
        d.getUTCMonth(),
        d.getUTCDate(),
        d.getUTCHours(),
        d.getUTCMinutes(),
        d.getUTCSeconds(),
        d.getUTCMilliseconds()
    );
}

/** Formats the specified date using the format string. */
export function formatDate(d: Date, format: string): string {
    if (isNullOrUndefined(format) || format.length == 0 || format == "i") {
        return date.toString();
    }

    if (format == "id") {
        return date.toDateString();
    }

    if (format == "it") {
        return date.toTimeString();
    }

    return netFormatDate(date, format);
}

const DateFormatInfo = {
    amDesignator: "AM",
    pmDesignator: "PM",

    dateSeparator: "/",
    timeSeparator: ":",

    gmtDateTimePattern: "ddd, dd MMM yyyy HH:mm:ss 'GMT'",
    universalDateTimePattern: "yyyy-MM-dd HH:mm:ssZ",
    sortableDateTimePattern: "yyyy-MM-ddTHH:mm:ss",
    dateTimePattern: "dddd, MMMM dd, yyyy h:mm:ss tt",

    longDatePattern: "dddd, MMMM dd, yyyy",
    shortDatePattern: "M/d/yyyy",

    longTimePattern: "h:mm:ss tt",
    shortTimePattern: "h:mm tt",

    firstDayOfWeek: 0,
    dayNames: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    shortDayNames: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    minimizedDayNames: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],

    monthNames: [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
        ""
    ],
    shortMonthNames: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", ""]
};

export function netFormatDate(dt: Date, format: string): string {
    if (format.length == 1) {
        switch (format) {
            case "f":
                format = DateFormatInfo.longDatePattern + " " + DateFormatInfo.shortTimePattern;
                break;
            case "F":
                format = DateFormatInfo.dateTimePattern;
                break;

            case "d":
                format = DateFormatInfo.shortDatePattern;
                break;
            case "D":
                format = DateFormatInfo.longDatePattern;
                break;

            case "t":
                format = DateFormatInfo.shortTimePattern;
                break;
            case "T":
                format = DateFormatInfo.longTimePattern;
                break;

            case "g":
                format = DateFormatInfo.shortDatePattern + " " + DateFormatInfo.shortTimePattern;
                break;
            case "G":
                format = DateFormatInfo.shortDatePattern + " " + DateFormatInfo.longTimePattern;
                break;

            case "R":
            case "r":
                DateFormatInfo = ss_CultureInfo.InvariantCulture.dateTimeFormat;
                format = DateFormatInfo.gmtDateTimePattern;
                break;
            case "u":
                format = DateFormatInfo.universalDateTimePattern;
                break;
            case "U":
                format = DateFormatInfo.dateTimePattern;
                dt = new Date(
                    dt.getUTCFullYear(),
                    dt.getUTCMonth(),
                    dt.getUTCDate(),
                    dt.getUTCHours(),
                    dt.getUTCMinutes(),
                    dt.getUTCSeconds(),
                    dt.getUTCMilliseconds()
                );
                break;

            case "s":
                format = DateFormatInfo.sortableDateTimePattern;
                break;
        }
    }

    if (format.charAt(0) == "%") {
        format = format.substr(1);
    }

    if (!Date._formatRE) {
        Date._formatRE = /'.*?[^\\]'|dddd|ddd|dd|d|MMMM|MMM|MM|M|yyyy|yy|y|hh|h|HH|H|mm|m|ss|s|tt|t|fff|ff|f|zzz|zz|z/g;
    }

    var re = Date._formatRE;
    var sb = new StringBuilder();

    re.lastIndex = 0;
    while (true) {  // eslint-disable-line no-constant-condition
        var index = re.lastIndex;
        var match = re.exec(format);

        sb.append(format.slice(index, match ? match.index : format.length));
        if (!match) {
            break;
        }

        var fs = match[0];
        var part = fs;
        switch (fs) {
            case "dddd":
                part = DateFormatInfo.dayNames[dt.getDay()];
                break;
            case "ddd":
                part = DateFormatInfo.shortDayNames[dt.getDay()];
                break;
            case "dd":
                part = padLeftString(dt.getDate().toString(), 2, 0x30);
                break;
            case "d":
                part = dt.getDate();
                break;
            case "MMMM":
                part = DateFormatInfo.monthNames[dt.getMonth()];
                break;
            case "MMM":
                part = DateFormatInfo.shortMonthNames[dt.getMonth()];
                break;
            case "MM":
                part = padLeftString((dt.getMonth() + 1).toString(), 2, 0x30);
                break;
            case "M":
                part = dt.getMonth() + 1;
                break;
            case "yyyy":
                part = dt.getFullYear();
                break;
            case "yy":
                part = padLeftString((dt.getFullYear() % 100).toString(), 2, 0x30);
                break;
            case "y":
                part = dt.getFullYear() % 100;
                break;
            case "h":
            case "hh":
                part = dt.getHours() % 12;
                if (!part) {
                    part = "12";
                } else if (fs == "hh") {
                    part = padLeftString(part.toString(), 2, 0x30);
                }
                break;
            case "HH":
                part = padLeftString(dt.getHours().toString(), 2, 0x30);
                break;
            case "H":
                part = dt.getHours();
                break;
            case "mm":
                part = padLeftString(dt.getMinutes().toString(), 2, 0x30);
                break;
            case "m":
                part = dt.getMinutes();
                break;
            case "ss":
                part = padLeftString(dt.getSeconds().toString(), 2, 0x30);
                break;
            case "s":
                part = dt.getSeconds();
                break;
            case "t":
            case "tt":
                part = dt.getHours() < 12 ? DateFormatInfo.amDesignator : DateFormatInfo.pmDesignator;
                if (fs == "t") {
                    part = part.charAt(0);
                }
                break;
            case "fff":
                part = padLeftString(dt.getMilliseconds().toString(), 3, 0x30);
                break;
            case "ff":
                part = padLeftString(dt.getMilliseconds().toString(), 3).substr(0, 2);
                break;
            case "f":
                part = padLeftString(dt.getMilliseconds().toString(), 3).charAt(0);
                break;
            case "z":
                part = dt.getTimezoneOffset() / 60;
                part = (part >= 0 ? "-" : "+") + Math.floor(Math.abs(part));
                break;
            case "zz":
            case "zzz":
                part = dt.getTimezoneOffset() / 60;
                part = (part >= 0 ? "-" : "+") + Math.floor(padLeftString(Math.abs(part)).toString(), 2, 0x30);
                if (fs == "zzz") {
                    part +=
                        DateFormatInfo.timeSeparator +
                        Math.abs(padLeftString(dt.getTimezoneOffset() % 60).toString(), 2, 0x30);
                }
                break;
            default:
                if (part.charAt(0) == "'") {
                    part = part.substr(1, part.length - 2).replace(/\\'/g, "'");
                }
                break;
        }
        sb.append(part);
    }

    return sb.toString();
}
