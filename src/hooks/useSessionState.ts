import { useCallback, useState } from "react";
import type { PageName, SessionData, SessionState } from "src/types";
import type { UserName } from "src/utils/usernames";

/**
 * Extracts session data from the current URL's query parameters. If a parameter
 * is provided, it must be valid; otherwise, return null.
 *
 * @returns A fully parsed SessionData's Props object.
 * @throws Error if a provided parameter is invalid.
 */
export function useSessionState(): SessionState {
    const { origin, pathname, search } = window.location;
    const searchParams = new URLSearchParams(search);

    const defaultPage = (
        searchParams.get("page") ?? "Home"
    ).toLowerCase() as PageName;
    const defaultUsername = (
        searchParams.get("username") ?? "ptprashanttripathi"
    ).toLowerCase() as UserName;

    const [data, setData] = useState<SessionData>({
        url: origin + pathname,
        page: defaultPage,
        username: defaultUsername,
        load_timestamp: new Date(),
        holding_trands_data: [],
        current_holding_data: [],
        dividend_data: [],
        profit_loss_data: [],
    });

    const updateData = useCallback((partial: Partial<SessionData>) => {
        setData(prev => ({ ...prev, ...partial }));
    }, []);

    return {
        data,
        setData,
        updateData,
    };
}
