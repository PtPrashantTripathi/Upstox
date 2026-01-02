const About: React.FC = () => {
    return (
        <div className="container">
            <div className="row">
                <div className="col">
                    <div className="card">
                        <img
                            className="card-img-top"
                            src="img/portfolio_tracker_header.png"
                            alt="Header"
                        />
                        <div className="card-header">
                            <h3 className="card-title">Description</h3>
                        </div>

                        <div className="card-body">
                            <p>
                                I've just completed an exciting ETL journey,
                                leveraging the power of Medallion architecture!
                                🚀 This Python notebook seamlessly extracts,
                                transforms, and loads data from my Upstox
                                trading account into a multi-tiered storage
                                system: BRONZE, SILVER, and GOLD layers. It's a
                                powerful way to enhance data management,
                                analytics, and decision-making in my trading
                                activities.
                            </p>
                            <p>
                                <strong>Key Highlights:</strong>
                            </p>
                            <p>
                                📊
                                <strong>Medallion Architecture</strong>:
                                Designed to efficiently handle data at scale,
                                ensuring robust ETL processes that can grow with
                                my trading data needs.
                            </p>
                            <p>
                                🔗
                                <strong>Upstox Integration</strong>: Seamlessly
                                connect with my Upstox trading account to
                                retrieve real-time and historical data.
                            </p>
                            <p>
                                🛠️ <strong>ETL Workflow</strong>: Perform data
                                extraction, apply transformations, and load the
                                processed data into multiple layers to
                                facilitate various analytics and reporting
                                needs.
                            </p>
                            <p>
                                📈
                                <strong>BRONZE, SILVER, GOLD Layers</strong>:
                                Structured storage tiers for raw data (BRONZE),
                                cleaned and transformed data (SILVER), and
                                curated data ready for analysis (GOLD).
                            </p>
                            <p>
                                📊
                                <strong>Presentation Layer</strong>: Another
                                companion notebook creates interactive
                                visualizations and insights from the GOLD layer
                                data, making it easier to understand my trading
                                performance and make informed decisions.
                            </p>
                            <p>
                                📓
                                <strong>Educational Tool</strong>: A valuable
                                resource for traders looking to optimize their
                                data analysis workflow.
                            </p>
                            <p>
                                👩‍💼
                                <strong>Financial Decision Support</strong>:
                                Empowering traders with data-driven insights to
                                improve decision-making and optimize their
                                trading strategies.
                            </p>
                            <p>
                                <strong>
                                    Stay tuned for the upcoming presentation
                                    layer notebook! 📊💡
                                </strong>
                            </p>
                            <p>
                                Feel free to explore, contribute, or share this
                                notebook with fellow traders. Let's navigate the
                                world of data-driven trading together! 📈💰
                            </p>
                        </div>
                        <div className="card-footer clearfix">
                            <p>
                                <strong>
                                    #DataAnalytics #TradingStrategies
                                    #MedallionArchitecture #ETLProcess
                                    #UpstoxData #DataDrivenDecisions
                                    #FinanceTech #DataInsights
                                </strong>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default About;
