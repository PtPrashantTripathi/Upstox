// Utility function for number formatting
export function priceFormat(value: string | number, short = false): string {
    const sign = Number(value) >= 0 ? "" : "-";
    value = parseFloat(String(value));
    if (short) {
        value = Math.abs(value);
        if (value >= 1e7) return `${sign}₹${(value / 1e7).toFixed(2)}Cr`;
        if (value >= 1e5) return `${sign}₹${(value / 1e5).toFixed(2)}L`;
        if (value >= 1e3) return `${sign}₹${(value / 1e3).toFixed(2)}K`;
    }
    return value.toLocaleString("en-IN", {
        maximumFractionDigits: 2,
        style: "currency",
        currency: "INR",
    });
}

// Utility function for parsing numbers
export function parseNum(value: string | number): number {
    return parseFloat(String(value)) === parseInt(String(value))
        ? parseInt(String(value))
        : parseFloat(parseFloat(String(value)).toFixed(2));
}

// Utility function to calculate days between dates
export function calcDays(
    date1: string | number | Date,
    date2: string | number | Date = new Date()
): number {
    const firstDate = new Date(date1);
    const secondDate = new Date(date2);
    const differenceInDays = Math.abs(
        Math.floor(
            (secondDate.getTime() - firstDate.getTime()) / (1000 * 60 * 60 * 24)
        )
    );
    return differenceInDays;
}
