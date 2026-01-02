import { useSessionContext } from "../../contexts/SessionContext";
import PNLSummary from "./pnl_summary";
import ProfitLossTable from "./profit_loss_table";

const ProfitAndLoss: React.FC = () => {
    const session = useSessionContext("profit_loss_data");

    if (session.data.profit_loss_data.length > 0) {
        return (
            <div className="container">
                <div className="row" id="PNLSummary">
                    <PNLSummary data={session.data.profit_loss_data} />
                </div>
                <div className="row">
                    <div className="col-12">
                        <div className="card">
                            <div className="card-header">
                                <h3 className="card-title">Profit and Loss</h3>
                            </div>
                            <div className="card-body p-0">
                                <div className="table-responsive">
                                    <ProfitLossTable
                                        data={session.data.profit_loss_data}
                                    />
                                </div>
                            </div>
                            <div className="card-footer clearfix" id="footnote">
                                <span>
                                    Brokerage fees may vary depending on the
                                    broker. Please confirm with your broker for
                                    accurate rates.
                                </span>
                                <a className="btn btn-sm btn-secondary float-right">
                                    View All Orders
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
};

export default ProfitAndLoss;
