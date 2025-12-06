export interface PoliticalPositionRequest {
    usuario: string;
    x: number;
    y: number;
}

export interface PoliticalPositionResponse {
    id: string;
    usuario: string;
    discordId: string;
    name: string;
    x: number;
    y: number;
    createdAt: Date;
    updatedAt: Date;
}

export interface GraphDataPoint {
    usuario: string;
    name: string;
    x: number;
    y: number;
}
