package com.butecobot.challenge.service;

import com.butecobot.challenge.model.Challenge;
import com.butecobot.challenge.model.ChallengeStatus;
import com.butecobot.challenge.repository.ChallengeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class ChallengeService {

    @Autowired
    private ChallengeRepository challengeRepository;

    /**
     * Create a new challenge
     */
    @Transactional
    public Challenge createChallenge(String challengerId, String challengedId, String channelId, String description) {
        // Validate that user is not challenging themselves
        if (challengerId.equals(challengedId)) {
            throw new IllegalArgumentException("You cannot challenge yourself!");
        }

        // Check if there's already an active challenge between these users
        Optional<Challenge> existingChallenge = challengeRepository.findActiveChallengesBetweenUsers(
                challengerId, challengedId, ChallengeStatus.ACTIVE);
        
        if (existingChallenge.isPresent()) {
            throw new IllegalStateException("There is already an active challenge between these users!");
        }

        Challenge challenge = new Challenge(challengerId, challengedId, channelId, description);
        return challengeRepository.save(challenge);
    }

    /**
     * Accept a pending challenge
     */
    @Transactional
    public Challenge acceptChallenge(Long challengeId) {
        Challenge challenge = challengeRepository.findById(challengeId)
                .orElseThrow(() -> new IllegalArgumentException("Challenge not found!"));

        if (challenge.getStatus() != ChallengeStatus.PENDING) {
            throw new IllegalStateException("Only pending challenges can be accepted!");
        }

        challenge.setStatus(ChallengeStatus.ACTIVE);
        return challengeRepository.save(challenge);
    }

    /**
     * Reject a pending challenge
     */
    @Transactional
    public Challenge rejectChallenge(Long challengeId) {
        Challenge challenge = challengeRepository.findById(challengeId)
                .orElseThrow(() -> new IllegalArgumentException("Challenge not found!"));

        if (challenge.getStatus() != ChallengeStatus.PENDING) {
            throw new IllegalStateException("Only pending challenges can be rejected!");
        }

        challenge.setStatus(ChallengeStatus.REJECTED);
        return challengeRepository.save(challenge);
    }

    /**
     * Increment score for a user in a challenge
     */
    @Transactional
    public Challenge incrementScore(Long challengeId, String userId) {
        Challenge challenge = challengeRepository.findById(challengeId)
                .orElseThrow(() -> new IllegalArgumentException("Challenge not found!"));

        if (challenge.getStatus() != ChallengeStatus.ACTIVE) {
            throw new IllegalStateException("Only active challenges can have scores updated!");
        }

        // Determine which score to increment
        if (challenge.getChallengerId().equals(userId)) {
            challenge.setChallengerScore(challenge.getChallengerScore() + 1);
        } else if (challenge.getChallengedId().equals(userId)) {
            challenge.setChallengedScore(challenge.getChallengedScore() + 1);
        } else {
            throw new IllegalArgumentException("User is not part of this challenge!");
        }

        return challengeRepository.save(challenge);
    }

    /**
     * Close an active challenge
     */
    @Transactional
    public Challenge closeChallenge(Long challengeId) {
        Challenge challenge = challengeRepository.findById(challengeId)
                .orElseThrow(() -> new IllegalArgumentException("Challenge not found!"));

        if (challenge.getStatus() != ChallengeStatus.ACTIVE) {
            throw new IllegalStateException("Only active challenges can be closed!");
        }

        challenge.setStatus(ChallengeStatus.COMPLETED);
        challenge.setCompletedAt(LocalDateTime.now());
        return challengeRepository.save(challenge);
    }

    /**
     * Get challenge by ID
     */
    public Challenge getChallengeById(Long challengeId) {
        return challengeRepository.findById(challengeId)
                .orElseThrow(() -> new IllegalArgumentException("Challenge not found!"));
    }

    /**
     * Get all active challenges for a user
     */
    public List<Challenge> getActiveChallengesForUser(String userId) {
        return challengeRepository.findByUserIdAndStatus(userId, ChallengeStatus.ACTIVE);
    }

    /**
     * Get all pending challenges for a user (where they are the challenged party)
     */
    public List<Challenge> getPendingChallengesForUser(String userId) {
        return challengeRepository.findByUserIdAndStatus(userId, ChallengeStatus.PENDING);
    }

    /**
     * Get all active challenges in a channel
     */
    public List<Challenge> getActiveChallengesInChannel(String channelId) {
        return challengeRepository.findByChannelIdAndStatus(channelId, ChallengeStatus.ACTIVE);
    }

    /**
     * Get all challenges for a user
     */
    public List<Challenge> getAllChallengesForUser(String userId) {
        return challengeRepository.findAllByUserId(userId);
    }
}
