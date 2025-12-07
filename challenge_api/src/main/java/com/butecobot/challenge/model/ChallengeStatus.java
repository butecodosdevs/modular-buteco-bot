package com.butecobot.challenge.model;

public enum ChallengeStatus {
    PENDING,    // Challenge created, waiting for acceptance
    ACTIVE,     // Challenge accepted and ongoing
    COMPLETED,  // Challenge finished
    REJECTED    // Challenge was rejected
}
