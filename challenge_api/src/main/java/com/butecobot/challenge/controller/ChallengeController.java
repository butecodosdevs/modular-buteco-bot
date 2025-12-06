package com.butecobot.challenge.controller;

import com.butecobot.challenge.dto.ChallengeResponse;
import com.butecobot.challenge.dto.CreateChallengeRequest;
import com.butecobot.challenge.dto.IncrementScoreRequest;
import com.butecobot.challenge.model.Challenge;
import com.butecobot.challenge.service.ChallengeService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/challenge")
public class ChallengeController {

    @Autowired
    private ChallengeService challengeService;

    /**
     * Create a new challenge
     */
    @PostMapping("/create")
    public ResponseEntity<?> createChallenge(@Valid @RequestBody CreateChallengeRequest request) {
        try {
            Challenge challenge = challengeService.createChallenge(
                    request.getChallengerId(),
                    request.getChallengedId(),
                    request.getChannelId(),
                    request.getDescription()
            );
            return ResponseEntity.status(HttpStatus.CREATED).body(new ChallengeResponse(challenge));
        } catch (IllegalArgumentException | IllegalStateException e) {
            Map<String, String> error = new HashMap<>();
            error.put("detail", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
        }
    }

    /**
     * Accept a challenge
     */
    @PostMapping("/{id}/accept")
    public ResponseEntity<?> acceptChallenge(@PathVariable Long id) {
        try {
            Challenge challenge = challengeService.acceptChallenge(id);
            return ResponseEntity.ok(new ChallengeResponse(challenge));
        } catch (IllegalArgumentException e) {
            Map<String, String> error = new HashMap<>();
            error.put("detail", e.getMessage());
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
        } catch (IllegalStateException e) {
            Map<String, String> error = new HashMap<>();
            error.put("detail", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
        }
    }

    /**
     * Reject a challenge
     */
    @PostMapping("/{id}/reject")
    public ResponseEntity<?> rejectChallenge(@PathVariable Long id) {
        try {
            Challenge challenge = challengeService.rejectChallenge(id);
            return ResponseEntity.ok(new ChallengeResponse(challenge));
        } catch (IllegalArgumentException e) {
            Map<String, String> error = new HashMap<>();
            error.put("detail", e.getMessage());
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
        } catch (IllegalStateException e) {
            Map<String, String> error = new HashMap<>();
            error.put("detail", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
        }
    }

    /**
     * Increment score for a user
     */
    @PostMapping("/{id}/increment")
    public ResponseEntity<?> incrementScore(@PathVariable Long id, @Valid @RequestBody IncrementScoreRequest request) {
        try {
            Challenge challenge = challengeService.incrementScore(id, request.getUserId());
            return ResponseEntity.ok(new ChallengeResponse(challenge));
        } catch (IllegalArgumentException e) {
            Map<String, String> error = new HashMap<>();
            error.put("detail", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
        } catch (IllegalStateException e) {
            Map<String, String> error = new HashMap<>();
            error.put("detail", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
        }
    }

    /**
     * Close a challenge
     */
    @PostMapping("/{id}/close")
    public ResponseEntity<?> closeChallenge(@PathVariable Long id) {
        try {
            Challenge challenge = challengeService.closeChallenge(id);
            return ResponseEntity.ok(new ChallengeResponse(challenge));
        } catch (IllegalArgumentException e) {
            Map<String, String> error = new HashMap<>();
            error.put("detail", e.getMessage());
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
        } catch (IllegalStateException e) {
            Map<String, String> error = new HashMap<>();
            error.put("detail", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
        }
    }

    /**
     * Get challenge by ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<?> getChallengeById(@PathVariable Long id) {
        try {
            Challenge challenge = challengeService.getChallengeById(id);
            return ResponseEntity.ok(new ChallengeResponse(challenge));
        } catch (IllegalArgumentException e) {
            Map<String, String> error = new HashMap<>();
            error.put("detail", e.getMessage());
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
        }
    }

    /**
     * Get active challenges for a user
     */
    @GetMapping("/user/{userId}/active")
    public ResponseEntity<List<ChallengeResponse>> getActiveChallengesForUser(@PathVariable String userId) {
        List<Challenge> challenges = challengeService.getActiveChallengesForUser(userId);
        List<ChallengeResponse> responses = challenges.stream()
                .map(ChallengeResponse::new)
                .collect(Collectors.toList());
        return ResponseEntity.ok(responses);
    }

    /**
     * Get pending challenges for a user
     */
    @GetMapping("/user/{userId}/pending")
    public ResponseEntity<List<ChallengeResponse>> getPendingChallengesForUser(@PathVariable String userId) {
        List<Challenge> challenges = challengeService.getPendingChallengesForUser(userId);
        List<ChallengeResponse> responses = challenges.stream()
                .map(ChallengeResponse::new)
                .collect(Collectors.toList());
        return ResponseEntity.ok(responses);
    }

    /**
     * Get all challenges for a user
     */
    @GetMapping("/user/{userId}/all")
    public ResponseEntity<List<ChallengeResponse>> getAllChallengesForUser(@PathVariable String userId) {
        List<Challenge> challenges = challengeService.getAllChallengesForUser(userId);
        List<ChallengeResponse> responses = challenges.stream()
                .map(ChallengeResponse::new)
                .collect(Collectors.toList());
        return ResponseEntity.ok(responses);
    }

    /**
     * Get active challenges in a channel
     */
    @GetMapping("/channel/{channelId}/active")
    public ResponseEntity<List<ChallengeResponse>> getActiveChallengesInChannel(@PathVariable String channelId) {
        List<Challenge> challenges = challengeService.getActiveChallengesInChannel(channelId);
        List<ChallengeResponse> responses = challenges.stream()
                .map(ChallengeResponse::new)
                .collect(Collectors.toList());
        return ResponseEntity.ok(responses);
    }
}
