#!/bin/bash
# Gather context for git commit decisions

echo '$ pwd'
pwd

echo ''
echo '$ git diff --cached --name-only'
git diff --cached --name-only

echo ''
echo '$ git diff --cached --stat'
git diff --cached --stat

echo ''
echo '$ git log --oneline -n 5'
git log --oneline -n 5

echo ''
echo '$ git status --short'
git status --short

echo ''
echo '$ git diff --cached'
git diff --cached
