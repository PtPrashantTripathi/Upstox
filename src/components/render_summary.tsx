interface props {
    summaryItems: {
        value: string;
        label: string;
        href?: string;
        iconClass: string;
        colorClass: string;
    }[];
}

const RenderSummary: React.FC<props> = ({ summaryItems }) => {
    return summaryItems.map(item => (
        <div className="col-lg-3 col-6" key={item.label}>
            <div className={`small-box ${item.colorClass}`}>
                <div className="inner">
                    <h4>{item.value}</h4>
                    <h6>{item.label}</h6>
                </div>
                <div className="icon">
                    <i className={item.iconClass}></i>
                </div>
                <a href={item.href} className="small-box-footer">
                    More info <i className="fas fa-arrow-circle-right"></i>
                </a>
            </div>
        </div>
    ));
};

export default RenderSummary;
