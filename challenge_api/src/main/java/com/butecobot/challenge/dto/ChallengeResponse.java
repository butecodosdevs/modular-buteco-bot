package com.butecobot.challenge.dto;

import com.butecobot.challenge.model.Challenge;
import com.butecobot.challenge.model.ChallengeStatus;

import java.time.LocalDateTime;

public class ChallengeResponse {

    private Long id;
    private String challengerId;
    private String challengedId;
    private String channelId;
    private ChallengeStatus status;
    private Integer challengerScore;
    private Integer challengedScore;
    private String description;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private LocalDateTime completedAt;

    // Constructor from Challenge entity
    public ChallengeResponse(Challenge challenge) {
        this.id = challenge.getId();
        this.challengerId = challenge.getChallengerId();
        this.challengedId = challenge.getChallengedId();
        this.channelId = challenge.getChannelId();
        this.status = challenge.getStatus();
        this.challengerScore = challenge.getChallengerScore();
        this.challengedScore = challenge.getChallengedScore();
        this.description = challenge.getDescription();
        this.createdAt = challenge.getCreatedAt();
        this.updatedAt = challenge.getUpdatedAt();
        this.completedAt = challenge.getCompletedAt();
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

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

    public ChallengeStatus getStatus() {
        return status;
    }

    public void setStatus(ChallengeStatus status) {
        this.status = status;
    }

    public Integer getChallengerScore() {
        return challengerScore;
    }

    public void setChallengerScore(Integer challengerScore) {
        this.challengerScore = challengerScore;
    }

    public Integer getChallengedScore() {
        return challengedScore;
    }

    public void setChallengedScore(Integer challengedScore) {
        this.challengedScore = challengedScore;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    public LocalDateTime getCompletedAt() {
        return completedAt;
    }

    public void setCompletedAt(LocalDateTime completedAt) {
        this.completedAt = completedAt;
    }
}
