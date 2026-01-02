import type { UserName } from "../utils/usernames";

export interface HoldingTrands {
    close: number;
    date: string;
    high: number;
    holding: number;
    low: number;
    open: number;
}
export interface CurrentHolding {
    amount: number;
    close_amount: number;
    close_price: number;
    datetime: string;
    exchange: string;
    pnl_amount: number;
    price: number;
    quantity: number;
    scrip_name: string;
    segment: string;
    side: string;
    symbol: string;
}
export interface Dividend {
    date: string;
    dividend_amount: number;
    financial_year: string;
    segment: string;
    symbol: string;
}
export interface ProfitLoss {
    brokerage: number;
    close_amount: number;
    close_datetime: string;
    close_price: number;
    close_side: string;
    exchange: string;
    open_amount: number;
    open_datetime: string;
    open_price: number;
    open_side: string;
    pnl_amount: number;
    pnl_percentage: number;
    position: string;
    quantity: number;
    scrip_name: string;
    segment: string;
    symbol: string;
    days: number;
}
export type PageName =
    | "home"
    | "current_holding"
    | "profit_and_loss"
    | "dividend"
    | "about";

export interface SessionData {
    url: string;
    page: PageName;
    username: UserName;
    load_timestamp: Date;
    holding_trands_data: HoldingTrands[];
    current_holding_data: CurrentHolding[];
    dividend_data: Dividend[];
    profit_loss_data: ProfitLoss[];
}

export interface SessionState {
    data: SessionData;
    setData: React.Dispatch<React.SetStateAction<SessionData>>;
    updateData: (data: Partial<SessionData>) => void;
}
