import React from "react";

import type { CurrentHolding } from "../../types";
import { calcDays, parseNum, priceFormat } from "../../utils";

interface Props {
    data: CurrentHolding[];
}

/** Load current holding table */
const CurrentHoldingTable: React.FC<Props> = ({ data }) => {
    const headers = [
        "Stock Name",
        "Qty.",
        "Avg Price",
        "Invested Value",
        "CMP Price",
        "Current Value",
        "Unrealized PNL",
        "PNL Percentage",
        "Holding Days",
    ];

    const grouped = data.reduce(
        (acc, item) => {
            const key = `${item.segment}-${item.exchange}-${item.symbol}`;
            if (!acc[key]) {
                acc[key] = {
                    key,
                    scrip_name: item.scrip_name,
                    symbol: item.symbol,
                    exchange: item.exchange,
                    segment: item.segment,
                    total_quantity: 0,
                    total_amount: 0,
                    close_price: item.close_price,
                    min_datetime: new Date(item.datetime),
                };
            }

            acc[key].total_quantity += item.quantity;
            acc[key].total_amount += item.amount;
            acc[key].min_datetime = new Date(
                Math.min(
                    acc[key].min_datetime.getTime(),
                    new Date(item.datetime).getTime()
                )
            );

            return acc;
        },
        {} as Record<
            string,
            {
                key: string;
                scrip_name: string;
                symbol: string;
                exchange: string;
                segment: string;
                total_quantity: number;
                total_amount: number;
                close_price: number;
                min_datetime: Date;
            }
        >
    );

    const currentHoldingData = Object.values(grouped)
        .map(record => {
            const { total_quantity, total_amount, close_price } = record;
            const close_amount = close_price * total_quantity;
            return {
                ...record,
                avg_price: total_quantity ? total_amount / total_quantity : 0,
                close_amount,
                pnl_amount: close_amount - total_amount,
            };
        })
        .sort((a, b) => a.key.localeCompare(b.key));

    return (
        <table
            className="table m-0 table-bordered table-striped"
            id="CurrentHoldingTable">
            <thead>
                <tr>
                    {headers.map(header => (
                        <th key={header}>{header}</th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {currentHoldingData.map(record => {
                    const pnlClass =
                        record.pnl_amount < 0 ? "text-danger" : "text-success";
                    const pnlPercentage =
                        (record.pnl_amount * 100) / record.total_amount;

                    return (
                        <tr key={record.key}>
                            <td>
                                {record.segment === "EQ"
                                    ? `${record.symbol} (${record.segment})`
                                    : `${record.scrip_name} (${record.segment})`}
                            </td>
                            <td>{parseNum(record.total_quantity)}</td>
                            <td>{priceFormat(record.avg_price)}</td>
                            <td>{priceFormat(record.total_amount)}</td>
                            <td className={pnlClass}>
                                {priceFormat(record.close_price)}
                            </td>
                            <td className={pnlClass}>
                                {priceFormat(record.close_amount)}
                            </td>
                            <td className={pnlClass}>
                                {priceFormat(record.pnl_amount)}
                            </td>
                            <td className={pnlClass}>
                                {record.pnl_amount >= 0 ? "+" : ""}
                                {parseNum(pnlPercentage)}%
                            </td>
                            <td>{calcDays(record.min_datetime)}</td>
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
};

export default CurrentHoldingTable;
