import RenderSummary from "../../components/render_summary";
import type { CurrentHolding } from "../../types";
import { parseNum, priceFormat } from "../../utils";

interface Props {
    data: CurrentHolding[];
}

/** Function to calculate profit/loss summary */
const CurrentHoldingSummary: React.FC<Props> = ({ data }) => {
    const investedValue = data.reduce((sum, record) => sum + record.amount, 0);
    const currentValue = data.reduce(
        (sum, record) => sum + record.close_amount,
        0
    );
    const pnlValue = data.reduce((sum, record) => sum + record.pnl_amount, 0);

    const pnlClass = pnlValue > 0 ? "bg-success" : "bg-danger";
    const pnlIcon = pnlValue > 0 ? "▲" : "▼";

    return (
        <RenderSummary
            summaryItems={[
                {
                    value: priceFormat(currentValue),
                    label: "Total Assets Worth",
                    colorClass: "bg-info",
                    iconClass: "fas fa-coins",
                    href: "?page=current_holding#CurrentHoldingTable",
                },
                {
                    value: priceFormat(investedValue),
                    label: "Total Investment",
                    colorClass: "bg-warning",
                    iconClass: "fas fa-cart-shopping",
                    href: "?page=current_holding#CurrentHoldingTable",
                },
                {
                    value: priceFormat(pnlValue),
                    label: "Total P&L",
                    colorClass: pnlClass,
                    iconClass: "fas fa-chart-pie",
                    href: "?page=current_holding#CurrentHoldingTable",
                },
                {
                    value: `${pnlIcon} ${parseNum((pnlValue * 100) / investedValue)}%`,
                    label: "Overall Return",
                    colorClass: pnlClass,
                    iconClass: "fas fa-chart-line",
                    href: "?page=current_holding#CurrentHoldingTable",
                },
            ]}
        />
    );
};

export default CurrentHoldingSummary;
