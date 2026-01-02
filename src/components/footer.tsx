interface Props {
    date: Date;
}

const Footer: React.FC<Props> = ({ date }) => {
    return (
        <footer className="main-footer">
            <div className="row">
                <div className="col">
                    <b>Copyright</b> © 2023-
                    {date.getFullYear() + " "}
                    <a href="https://github.com/ptprashanttripathi/PortfolioTracker">
                        @PtPrashantTripathi
                    </a>
                    <br />
                    All rights reserved.
                </div>
                <div className="col text-right">
                    <strong>Last updated On : </strong>
                    {date.toLocaleString("en-IN", {
                        day: "2-digit",
                        month: "short",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                        hour12: true,
                        timeZone: "Asia/Calcutta",
                        timeZoneName: "short",
                    })}
                </div>
            </div>
        </footer>
    );
};
export default Footer;
