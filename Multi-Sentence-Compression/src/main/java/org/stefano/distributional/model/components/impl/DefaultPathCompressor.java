package org.stefano.distributional.model.components.impl;

import org.neo4j.graphalgo.GraphAlgoFactory;
import org.neo4j.graphalgo.PathFinder;
import org.neo4j.graphdb.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.stefano.distributional.model.components.GraphModel;
import org.stefano.distributional.model.components.PathCompressor;

import java.util.Iterator;
import java.util.Optional;
import java.util.Set;
import java.util.TreeSet;
import java.util.function.DoubleBinaryOperator;

import static java.util.Objects.requireNonNull;

/**
 * This class provides the default method to generate a compressive summary from a {@code word graph}.
 */
public final class DefaultPathCompressor implements PathCompressor {

    private static final Logger logger = LoggerFactory.getLogger(DefaultPathCompressor.class);

    @Override
    public Optional<String> compress(GraphDatabaseService graph, int maxDepth) {
        try (Transaction tx = graph.beginTx()) {
            long elapsed = System.nanoTime();
            logger.debug("Computing all the paths between START and END nodes and their costs...");
            int total = 0;
            Set<CostPath> paths = new TreeSet<>();
            PathFinder<Path> finder = GraphAlgoFactory.allPaths(EXPANDER, maxDepth);
            double minCost1 = Double.MAX_VALUE;
            double minCost2 = Double.MAX_VALUE;
            int count = 0;
            for (Path path : finder.findAllPaths(GraphModel.start(graph), GraphModel.end(graph))) {
//                logger.debug("Path length: {}...", path.length());
//                if (paths.size() > 1000) {
//                    break;
//                }
                if (path.length() >= PathCompressor.MIN_DEPTH && PathCompressor.hasVerb(path)) {
                    double cost = 0.0;
//                    logger.debug("Total {}", total);

                    if (count == 0) {
                        for (Relationship follows : path.relationships()) {
                            cost += (double) follows.getProperty("weight", 1.0);
//                            logger.debug("cost {}", cost);
                        }
//                        logger.debug("First cost {}", cost);
                        minCost1 = cost;
//                        logger.debug("First set minCost1 {}", minCost1);
                    }

                    else if (count == 1) {
                        for (Relationship follows : path.relationships()) {
                            cost += (double) follows.getProperty("weight", 1.0);
                        }
//                        logger.debug("Second cost {}", cost);
                        minCost1 = Math.min(minCost1, cost);
                        minCost2 = Math.max(minCost1, cost);
//                        logger.debug("Second set minCost1 {}", minCost1);
//                        logger.debug("Second set minCost2 {}", minCost2);
                    }

                    else {
                        for (Relationship follows : path.relationships()) {
                            cost += (double) follows.getProperty("weight", 1.0);
                            if (cost > minCost2) {
//                                logger.debug("break path cost: {}...", cost);
                                break;
                            }
                        }
//                        logger.debug("small path cost: {}...", cost);
                    }

                    if (cost <= minCost1) {
                        if (cost < minCost1){
                            minCost2 = minCost1;
                        }
                        minCost1 = cost;
                        paths.add(new CostPath(path, cost));
//                        logger.debug("Add path 1");
                    } else if (cost <= minCost2) {
                        minCost2 = cost;
                        paths.add(new CostPath(path, cost));
//                        logger.debug("Add path 2");
                    }
                    count += 1;
//                    logger.debug("final path cost: {}...", cost);

                }
                total += 1;
            }
            logger.info("{} valid path/s found (out of {} possible) in {} ms.",
                    paths.size(), total, String.format("%,.3f", elapsed / 1_000_000_000.0));
            if (paths.isEmpty()) {
                return Optional.empty();
            }
            logger.debug("Generating the compressive summary");
            if (paths.size() >= 2) {

                Iterator<CostPath> iterator = paths.iterator();
                Path path1 = iterator.next().getPath();
                Path path2 = iterator.next().getPath();

                requireNonNull(path1, "'path1' is null");
                requireNonNull(path2, "'path2' is null");

                String sentence1 = "";
                for (Node node : path1.nodes()) {
                    sentence1 = (sentence1 + " " + node.getProperty("word", "")).trim();
                }
                String sentence2 = "";
                for (Node node : path2.nodes()) {
                    sentence2 = (sentence2 + " " + node.getProperty("word", "")).trim();
                }
                String sentence = sentence1 + ".\n" + sentence2 + ".";
                if (!sentence.equals("\n")) {
                    return Optional.of(sentence);
                }
                return Optional.empty();
            }
            return PathCompressor.decode(paths.iterator().next().getPath());
        }
    }

//    @Override
//    public Optional<String> compress(GraphDatabaseService graph, int maxDepth) {
//        try (Transaction tx = graph.beginTx()) {
//            long elapsed = System.nanoTime();
//            logger.debug("Computing all the paths between START and END nodes and their costs...");
//            int total = 0;
//            Set<CostPath> paths = new TreeSet<>();
//            PathFinder<Path> finder = GraphAlgoFactory.allPaths(EXPANDER, maxDepth);
//            for (Path path : finder.findAllPaths(GraphModel.start(graph), GraphModel.end(graph))) {
//                if (path.length() >= PathCompressor.MIN_DEPTH && PathCompressor.hasVerb(path)) {
//                    double cost = 0.0;
//                    for (Relationship follows : path.relationships()) {
//                        cost += (double) follows.getProperty("weight", 1.0);
//                        logger.debug("cost {}", cost);
//                    }
//                    paths.add(new CostPath(path, cost));
//                }
//                total += 1;
//            }
//            logger.info("{} valid path/s found (out of {} possible) in {} ms.",
//                    paths.size(), total, String.format("%,.3f", elapsed / 1_000_000_000.0));
//            if (paths.isEmpty()) {
//                return Optional.empty();
//            }
//            logger.debug("Generating the compressive summary");
//            return PathCompressor.decode(paths.iterator().next().getPath());
//        }
//    }

}
