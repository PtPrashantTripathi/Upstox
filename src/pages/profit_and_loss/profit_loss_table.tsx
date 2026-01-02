import React from "react";

import type { ProfitLoss } from "../../types";
import { calcDays, parseNum, priceFormat } from "../../utils";

interface Props {
    data: ProfitLoss[];
}

const ProfitLossTable: React.FC<Props> = ({ data }) => {
    const grouped = data.reduce(
        (acc, record) => {
            const key = `${record.segment}-${record.exchange}-${record.symbol}`;

            if (record.segment === "FO") {
                record.close_price = record.pnl_amount / record.quantity;
                record.close_amount = record.pnl_amount;
                record.open_price = 0;
                record.open_amount = 0;
            }

            record.days = Math.floor(
                (new Date(record.close_datetime).getTime() -
                    new Date(record.open_datetime).getTime()) /
                    (1000 * 60 * 60 * 24)
            );

            if (!acc[key]) acc[key] = [];
            acc[key].push(record);
            return acc;
        },
        {} as Record<string, ProfitLoss[]>
    );

    const profitLossData = Object.entries(grouped).map(([_, group]) => {
        const initial = {
            quantity: 0,
            open_amount: 0,
            close_amount: 0,
            pnl: 0,
            brokerage: 0,
            min_time: Infinity,
            max_time: -Infinity,
        };

        const totals = group.reduce((sum, item) => {
            const openTime = new Date(item.open_datetime).getTime();
            const closeTime = new Date(item.close_datetime).getTime();

            return {
                quantity: sum.quantity + item.quantity,
                open_amount: sum.open_amount + item.open_amount,
                close_amount: sum.close_amount + item.close_amount,
                pnl: sum.pnl + item.pnl_amount,
                brokerage: sum.brokerage + item.brokerage,
                min_time: Math.min(sum.min_time, openTime),
                max_time: Math.max(sum.max_time, closeTime),
            };
        }, initial);

        return {
            segment: group[0].segment,
            exchange: group[0].exchange,
            symbol: group[0].symbol,
            quantity: totals.quantity,
            open_amount: totals.open_amount,
            close_amount: totals.close_amount,
            avg_price: totals.open_amount / totals.quantity,
            sell_price: totals.close_amount / totals.quantity,
            pnl: totals.pnl,
            brokerage: totals.brokerage,
            min_datetime: new Date(totals.min_time),
            max_datetime: new Date(totals.max_time),
            history: group,
        };
    });

    const headers = [
        "Stock Name",
        "Qty.",
        "Avg Price",
        "Sell Price",
        "Realized PNL",
        "PNL Percentage",
        <a href="#footnote">
            Brokerage<b>*</b>
        </a>,
        "Holding Days",
    ];

    return (
        <table
            className="table m-0 table-bordered table-striped"
            id="ProfitLossTable">
            <thead>
                <tr>
                    {headers.map((h, i) => (
                        <th key={i}>{h}</th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {profitLossData.map(record => {
                    const pnlClass =
                        record.pnl < 0 ? "text-danger" : "text-success";
                    const pnlPercent =
                        (record.pnl * 100) /
                        (record.avg_price * record.quantity);

                    return (
                        <tr key={`${record.symbol}-${record.segment}`}>
                            <td>{`${record.symbol} (${record.segment})`}</td>
                            <td>{parseNum(record.quantity)}</td>
                            <td>{priceFormat(record.avg_price)}</td>
                            <td>{priceFormat(record.sell_price)}</td>
                            <td className={pnlClass}>
                                {priceFormat(record.pnl)}
                            </td>
                            <td className={pnlClass}>
                                {record.pnl < 0 ? "" : "+"}
                                {parseNum(pnlPercent)}%
                            </td>
                            <td>{priceFormat(record.brokerage)}</td>
                            <td>
                                {calcDays(
                                    record.min_datetime,
                                    record.max_datetime
                                )}
                            </td>
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
};

export default ProfitLossTable;
