import axios from "axios";

export class BalanceService {
  balanceApi = axios.create({
    baseURL: Bun.env.BALANCE_API_URL || "http://localhost:5011",
    timeout: 5000,
  });

  async getUserBalance(clientId: string) {
    const response = this.balanceApi
      .get<{
        user_id: string;
        balance: number;
      }>(`/balance/${clientId}`)
      .then((res) => {
        console.log(res.data);

        return res.data;
      });

    return response;
  }
}
