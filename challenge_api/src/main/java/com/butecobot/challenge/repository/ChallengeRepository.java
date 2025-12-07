package com.butecobot.challenge.repository;

import com.butecobot.challenge.model.Challenge;
import com.butecobot.challenge.model.ChallengeStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ChallengeRepository extends JpaRepository<Challenge, Long> {

    // Find all active challenges for a user (either as challenger or challenged)
    @Query("SELECT c FROM Challenge c WHERE (c.challengerId = :userId OR c.challengedId = :userId) AND c.status = :status")
    List<Challenge> findByUserIdAndStatus(@Param("userId") String userId, @Param("status") ChallengeStatus status);

    // Find all challenges in a specific channel with a specific status
    List<Challenge> findByChannelIdAndStatus(String channelId, ChallengeStatus status);

    // Find active challenge between two users
    @Query("SELECT c FROM Challenge c WHERE ((c.challengerId = :user1 AND c.challengedId = :user2) OR (c.challengerId = :user2 AND c.challengedId = :user1)) AND c.status = :status")
    Optional<Challenge> findActiveChallengesBetweenUsers(@Param("user1") String user1, @Param("user2") String user2, @Param("status") ChallengeStatus status);

    // Find all challenges for a user
    @Query("SELECT c FROM Challenge c WHERE c.challengerId = :userId OR c.challengedId = :userId ORDER BY c.createdAt DESC")
    List<Challenge> findAllByUserId(@Param("userId") String userId);
}
