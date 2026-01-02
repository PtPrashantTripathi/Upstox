import RenderSummary from "../../components/render_summary";
import type { HoldingTrands } from "../../types";
import { parseNum, priceFormat } from "../../utils";

interface Props {
    data: HoldingTrands[];
}

/** Function to Financial Summary */
const FinancialSummary: React.FC<Props> = ({ data }) => {
    const latest_data = data.reduce((max, item) => {
        return new Date(item.date) > new Date(max.date) ? item : max;
    });
    const pnlValue = latest_data.close - latest_data.holding;
    const pnlClass = pnlValue > 0 ? "bg-success" : "bg-danger";
    const pnlIcon = pnlValue > 0 ? "▲" : "▼";

    return (
        <RenderSummary
            summaryItems={[
                {
                    // currentValue
                    value: priceFormat(latest_data.close),
                    label: "Total Assets Worth",
                    colorClass: "bg-info",
                    iconClass: "fas fa-coins",
                    href: "?page=current_holding#CurrentHoldingTable",
                },
                {
                    //investedValue
                    value: priceFormat(latest_data.holding),
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
                    value: `${pnlIcon} ${parseNum((pnlValue * 100) / latest_data.holding)}%`,
                    label: "Overall Return",
                    colorClass: pnlClass,
                    iconClass: "fas fa-chart-line",
                    href: "?page=current_holding#CurrentHoldingTable",
                },
            ]}
        />
    );
};

export default FinancialSummary;
