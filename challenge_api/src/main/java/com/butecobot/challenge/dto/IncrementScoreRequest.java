package com.butecobot.challenge.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class IncrementScoreRequest {

    @NotNull(message = "Challenge ID is required")
    private Long challengeId;

    @NotBlank(message = "User ID is required")
    private String userId;

    // Constructors
    public IncrementScoreRequest() {
    }

    public IncrementScoreRequest(Long challengeId, String userId) {
        this.challengeId = challengeId;
        this.userId = userId;
    }

    // Getters and Setters
    public Long getChallengeId() {
        return challengeId;
    }

    public void setChallengeId(Long challengeId) {
        this.challengeId = challengeId;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }
}
