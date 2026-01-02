import { useSessionContext } from "../../contexts/SessionContext";
import CurrentHoldingSummary from "./current_holding_summary";
import CurrentHoldingTable from "./current_holding_table";

const Home: React.FC = () => {
    const session = useSessionContext("current_holding_data");

    if (session.data.current_holding_data.length > 0) {
        return (
            <div className="container">
                <div className="row">
                    <CurrentHoldingSummary
                        data={session.data.current_holding_data}
                    />
                </div>

                <div className="row">
                    <div className="col-12">
                        <div className="card">
                            <div className="card-header">
                                <h3 className="card-title">
                                    Current Holding Table
                                </h3>
                            </div>
                            <div className="card-body p-0">
                                <div className="table-responsive">
                                    <CurrentHoldingTable
                                        data={session.data.current_holding_data}
                                    />
                                </div>
                            </div>
                            <div className="card-footer clearfix">
                                <a
                                    href="?page=current_holding#FinancialSummary"
                                    className="btn btn-sm btn-secondary float-right">
                                    View Summary
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
};

export default Home;
