import React from "react";

import type { Dividend } from "../../types";
import { priceFormat } from "../../utils";

interface Props {
    data: Dividend[];
}

const DividendTable: React.FC<Props> = ({ data }) => {
    // Extract unique financial years and sort them
    const uniqueFY = Array.from(
        new Set(data.map(item => item.financial_year))
    ).sort((a, b) => a.localeCompare(b));

    const headers = ["Stock Name", ...uniqueFY, "Total"];

    // Group and process dividend data
    const groupedData = data.reduce(
        (acc, item) => {
            const key = `${item.symbol} (${item.segment})`;
            if (!acc[key]) acc[key] = [];
            acc[key].push(item);
            return acc;
        },
        {} as Record<string, Dividend[]>
    );

    const stockWiseData = Object.entries(groupedData)
        .map(([symbol, group]) => {
            const yearDataMap = group.reduce(
                (map, item) => {
                    map[item.financial_year] =
                        (map[item.financial_year] || 0) + item.dividend_amount;
                    return map;
                },
                {} as Record<string, number>
            );

            return {
                symbol,
                dividend_amount: group.reduce(
                    (sum, item) => sum + item.dividend_amount,
                    0
                ),
                yearDataMap,
            };
        })
        .sort((a, b) => a.symbol.localeCompare(b.symbol));

    return (
        <table
            className="table m-0 table-bordered table-striped"
            id="ProfitLossTable">
            <thead>
                <tr>
                    {headers.map((header, i) => (
                        <th key={i}>{header}</th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {stockWiseData.map((record, idx) => (
                    <tr key={idx}>
                        <td>{record.symbol}</td>
                        {uniqueFY.map((fy, i) => (
                            <td
                                key={i}
                                className={
                                    record.yearDataMap[fy]
                                        ? "text-success"
                                        : "text-info"
                                }>
                                {record.yearDataMap[fy]
                                    ? priceFormat(record.yearDataMap[fy])
                                    : "-"}
                            </td>
                        ))}
                        <td className="text-success">
                            {priceFormat(record.dividend_amount)}
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

export default DividendTable;
