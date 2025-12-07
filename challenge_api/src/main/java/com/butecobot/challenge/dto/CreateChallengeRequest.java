package com.butecobot.challenge.dto;

import jakarta.validation.constraints.NotBlank;

public class CreateChallengeRequest {

    @NotBlank(message = "Challenger ID is required")
    private String challengerId;

    @NotBlank(message = "Challenged ID is required")
    private String challengedId;

    @NotBlank(message = "Channel ID is required")
    private String channelId;

    private String description;

    // Constructors
    public CreateChallengeRequest() {
    }

    public CreateChallengeRequest(String challengerId, String challengedId, String channelId, String description) {
        this.challengerId = challengerId;
        this.challengedId = challengedId;
        this.channelId = channelId;
        this.description = description;
    }

    // Getters and Setters
    public String getChallengerId() {
        return challengerId;
    }

    public void setChallengerId(String challengerId) {
        this.challengerId = challengerId;
    }

    public String getChallengedId() {
        return challengedId;
    }

    public void setChallengedId(String challengedId) {
        this.challengedId = challengedId;
    }

    public String getChannelId() {
        return channelId;
    }

    public void setChannelId(String channelId) {
        this.channelId = channelId;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }
}
