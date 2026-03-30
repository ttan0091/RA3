"""
AC State Tracker - Persistent state management for autonomous coding.

Manages all state across sessions including:
- Feature list tracking
- Execution state
- Progress logging
- Handoff packages
- Checkpoint management
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any


@dataclass
class Feature:
    """A single feature to implement."""
    id: str
    description: str
    category: str = "general"
    status: str = "pending"  # pending, in_progress, completed, blocked
    passes: bool = False
    priority: int = 5  # 1 = highest, 9 = lowest
    test_cases: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    estimated_effort: str = ""
    actual_effort: str = ""
    requirement_id: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    blockers: List[str] = field(default_factory=list)


@dataclass
class FeatureList:
    """Complete feature list for a project."""
    features: List[Feature] = field(default_factory=list)
    total: int = 0
    completed: int = 0
    in_progress: int = 0
    blocked: int = 0


@dataclass
class ExecutionState:
    """Current execution state."""
    session_id: str = ""
    iteration: int = 0
    status: str = "idle"  # idle, running, paused, completed, failed
    estimated_cost: float = 0.0
    consecutive_failures: int = 0
    current_feature: str = ""
    last_task: str = ""
    started_at: str = ""
    context_usage: float = 0.0


@dataclass
class MasterState:
    """Overall orchestration state."""
    project_id: str = ""
    objective: str = ""
    sessions_used: int = 0
    total_features: int = 0
    features_completed: int = 0
    current_phase: str = "initialization"
    last_handoff: str = ""


@dataclass
class Checkpoint:
    """A rollback checkpoint."""
    id: str
    name: str
    timestamp: str
    git_commit: str
    feature_list_snapshot: str
    execution_state_snapshot: str
    is_auto: bool = True


class StateTracker:
    """
    Persistent state management for autonomous coding.

    Usage:
        state = StateTracker(project_dir)
        await state.initialize()
        await state.update_feature("auth-001", passes=True)
    """

    FEATURE_LIST_FILE = "feature_list.json"
    EXECUTION_STATE_FILE = ".claude/autonomous-state.json"
    MASTER_STATE_FILE = ".claude/master-state.json"
    PROGRESS_FILE = "claude-progress.txt"
    LOG_FILE = ".claude/autonomous-log.jsonl"
    HANDOFF_DIR = ".claude/handoffs"
    CHECKPOINT_DIR = ".claude/checkpoints"

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir)
        self._feature_list: Optional[FeatureList] = None
        self._execution_state: Optional[ExecutionState] = None
        self._master_state: Optional[MasterState] = None

    async def initialize(self) -> None:
        """Initialize state tracker, loading existing state if present."""
        # Ensure directories exist
        (self.project_dir / ".claude").mkdir(parents=True, exist_ok=True)
        (self.project_dir / self.HANDOFF_DIR).mkdir(parents=True, exist_ok=True)
        (self.project_dir / self.CHECKPOINT_DIR).mkdir(parents=True, exist_ok=True)

        # Load existing state
        await self.load()

    async def load(self) -> Dict[str, Any]:
        """Load all state from files."""
        self._feature_list = await self._load_feature_list()
        self._execution_state = await self._load_execution_state()
        self._master_state = await self._load_master_state()

        return {
            "features": self._feature_list,
            "execution": self._execution_state,
            "master": self._master_state
        }

    async def save(self) -> None:
        """Save all state to files."""
        await self._save_feature_list()
        await self._save_execution_state()
        await self._save_master_state()
        await self._update_progress_file()

    # Feature List Operations

    async def get_features(self) -> FeatureList:
        """Get current feature list."""
        if not self._feature_list:
            self._feature_list = await self._load_feature_list()
        return self._feature_list

    async def update_feature(
        self,
        feature_id: str,
        passes: Optional[bool] = None,
        status: Optional[str] = None,
        actual_effort: Optional[str] = None,
        blockers: Optional[List[str]] = None
    ) -> Feature:
        """
        Update a feature's status.

        CRITICAL: passes can ONLY transition from false to true!
        """
        features = await self.get_features()

        for feature in features.features:
            if feature.id == feature_id:
                # Update passes (ONLY false → true allowed!)
                if passes is not None:
                    if feature.passes and not passes:
                        raise ValueError(
                            f"Cannot set passes=false for feature {feature_id}. "
                            "Features can only transition false → true."
                        )
                    if passes and not feature.passes:
                        feature.passes = True
                        feature.completed_at = datetime.utcnow().isoformat() + "Z"

                # Update status
                if status:
                    feature.status = status
                    if status == "in_progress" and not feature.started_at:
                        feature.started_at = datetime.utcnow().isoformat() + "Z"
                    elif status == "completed":
                        feature.completed_at = datetime.utcnow().isoformat() + "Z"

                # Update effort
                if actual_effort:
                    feature.actual_effort = actual_effort

                # Update blockers
                if blockers is not None:
                    feature.blockers = blockers

                await self._save_feature_list()
                return feature

        raise ValueError(f"Feature {feature_id} not found")

    async def add_feature(self, feature: Feature) -> None:
        """Add a new feature to the list."""
        features = await self.get_features()
        features.features.append(feature)
        features.total = len(features.features)
        await self._save_feature_list()

    async def get_next_feature(self) -> Optional[Feature]:
        """Get the next feature to work on based on priority and dependencies."""
        features = await self.get_features()

        completed_ids = {f.id for f in features.features if f.passes}

        for feature in features.features:
            if feature.passes:
                continue
            if feature.status == "blocked":
                continue

            # Check dependencies
            deps_met = all(dep in completed_ids for dep in feature.dependencies)
            if deps_met:
                return feature

        return None

    # Execution State Operations

    async def get_execution_state(self) -> ExecutionState:
        """Get current execution state."""
        if not self._execution_state:
            self._execution_state = await self._load_execution_state()
        return self._execution_state

    async def update_execution(self, **kwargs) -> ExecutionState:
        """Update execution state."""
        state = await self.get_execution_state()

        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)

        await self._save_execution_state()
        return state

    async def increment_iteration(self) -> int:
        """Increment iteration counter and return new value."""
        state = await self.get_execution_state()
        state.iteration += 1
        await self._save_execution_state()
        return state.iteration

    # Checkpoint Operations

    async def create_checkpoint(
        self,
        name: str = "",
        git_commit: bool = True
    ) -> Checkpoint:
        """Create a checkpoint for rollback."""
        import subprocess

        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        checkpoint_id = f"checkpoint-{timestamp}"

        # Get git commit
        commit_hash = ""
        if git_commit:
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True
                )
                commit_hash = result.stdout.strip()
            except Exception:
                pass

        # Create checkpoint directory
        checkpoint_dir = self.project_dir / self.CHECKPOINT_DIR / checkpoint_id
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Copy feature list
        feature_snapshot = checkpoint_dir / "feature_list.json"
        if (self.project_dir / self.FEATURE_LIST_FILE).exists():
            import shutil
            shutil.copy(
                self.project_dir / self.FEATURE_LIST_FILE,
                feature_snapshot
            )

        # Copy execution state
        state_snapshot = checkpoint_dir / "execution-state.json"
        if (self.project_dir / self.EXECUTION_STATE_FILE).exists():
            import shutil
            shutil.copy(
                self.project_dir / self.EXECUTION_STATE_FILE,
                state_snapshot
            )

        checkpoint = Checkpoint(
            id=checkpoint_id,
            name=name or f"auto-{timestamp}",
            timestamp=datetime.utcnow().isoformat() + "Z",
            git_commit=commit_hash,
            feature_list_snapshot=str(feature_snapshot),
            execution_state_snapshot=str(state_snapshot),
            is_auto=not bool(name)
        )

        # Save checkpoint metadata
        with open(checkpoint_dir / "metadata.json", 'w') as f:
            json.dump(asdict(checkpoint), f, indent=2)

        return checkpoint

    async def restore_checkpoint(self, checkpoint_id: str) -> None:
        """Restore state from a checkpoint."""
        import shutil

        checkpoint_dir = self.project_dir / self.CHECKPOINT_DIR / checkpoint_id

        if not checkpoint_dir.exists():
            raise ValueError(f"Checkpoint {checkpoint_id} not found")

        # Restore feature list
        feature_snapshot = checkpoint_dir / "feature_list.json"
        if feature_snapshot.exists():
            shutil.copy(feature_snapshot, self.project_dir / self.FEATURE_LIST_FILE)

        # Restore execution state
        state_snapshot = checkpoint_dir / "execution-state.json"
        if state_snapshot.exists():
            shutil.copy(state_snapshot, self.project_dir / self.EXECUTION_STATE_FILE)

        # Reload state
        await self.load()

    # Logging Operations

    async def log_activity(
        self,
        action: str,
        details: str = "",
        iteration: Optional[int] = None
    ) -> None:
        """Log activity to the autonomous log."""
        state = await self.get_execution_state()

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "iteration": iteration or state.iteration,
            "action": action,
            "details": details
        }

        log_path = self.project_dir / self.LOG_FILE
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(log_path, 'a') as f:
            f.write(json.dumps(entry) + "\n")

    # Handoff Operations

    async def save_handoff(self, data: Dict[str, Any]) -> str:
        """Save handoff package for next session."""
        handoff_dir = self.project_dir / self.HANDOFF_DIR
        handoff_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().isoformat() + "Z"
        state = await self.get_execution_state()
        features = await self.get_features()

        handoff = {
            "id": f"handoff-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            "timestamp": timestamp,
            "session_number": self._master_state.sessions_used if self._master_state else 1,
            "current_feature": state.current_feature,
            "features_completed": features.completed,
            "features_total": features.total,
            **data
        }

        # Save as current handoff
        with open(handoff_dir / "current.json", 'w') as f:
            json.dump(handoff, f, indent=2)

        return handoff["id"]

    async def load_handoff(self) -> Optional[Dict[str, Any]]:
        """Load current handoff package."""
        handoff_path = self.project_dir / self.HANDOFF_DIR / "current.json"

        if not handoff_path.exists():
            return None

        with open(handoff_path) as f:
            return json.load(f)

    async def clear_handoff(self) -> None:
        """Clear current handoff after successful resume."""
        handoff_path = self.project_dir / self.HANDOFF_DIR / "current.json"
        if handoff_path.exists():
            handoff_path.unlink()

    # Progress Summary

    async def get_progress(self) -> Dict[str, Any]:
        """Get progress summary."""
        features = await self.get_features()
        state = await self.get_execution_state()

        completed = sum(1 for f in features.features if f.passes)
        total = len(features.features)

        return {
            "completed": completed,
            "total": total,
            "percentage": round(completed / total * 100, 1) if total > 0 else 0,
            "current_feature": state.current_feature,
            "iteration": state.iteration,
            "status": state.status,
            "estimated_cost": state.estimated_cost
        }

    # Private Methods

    async def _load_feature_list(self) -> FeatureList:
        """Load feature list from file."""
        path = self.project_dir / self.FEATURE_LIST_FILE

        if not path.exists():
            return FeatureList()

        with open(path) as f:
            data = json.load(f)

        features = [Feature(**f) for f in data.get("features", [])]
        return FeatureList(
            features=features,
            total=len(features),
            completed=sum(1 for f in features if f.passes),
            in_progress=sum(1 for f in features if f.status == "in_progress"),
            blocked=sum(1 for f in features if f.status == "blocked")
        )

    async def _save_feature_list(self) -> None:
        """Save feature list to file."""
        if not self._feature_list:
            return

        # Update counts
        self._feature_list.total = len(self._feature_list.features)
        self._feature_list.completed = sum(
            1 for f in self._feature_list.features if f.passes
        )
        self._feature_list.in_progress = sum(
            1 for f in self._feature_list.features if f.status == "in_progress"
        )
        self._feature_list.blocked = sum(
            1 for f in self._feature_list.features if f.status == "blocked"
        )

        data = {
            "features": [asdict(f) for f in self._feature_list.features],
            "total": self._feature_list.total,
            "completed": self._feature_list.completed,
            "in_progress": self._feature_list.in_progress,
            "blocked": self._feature_list.blocked
        }

        with open(self.project_dir / self.FEATURE_LIST_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    async def _load_execution_state(self) -> ExecutionState:
        """Load execution state from file."""
        path = self.project_dir / self.EXECUTION_STATE_FILE

        if not path.exists():
            return ExecutionState()

        with open(path) as f:
            data = json.load(f)

        return ExecutionState(**data)

    async def _save_execution_state(self) -> None:
        """Save execution state to file."""
        if not self._execution_state:
            return

        path = self.project_dir / self.EXECUTION_STATE_FILE
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(asdict(self._execution_state), f, indent=2)

    async def _load_master_state(self) -> MasterState:
        """Load master state from file."""
        path = self.project_dir / self.MASTER_STATE_FILE

        if not path.exists():
            return MasterState()

        with open(path) as f:
            data = json.load(f)

        return MasterState(**data)

    async def _save_master_state(self) -> None:
        """Save master state to file."""
        if not self._master_state:
            return

        path = self.project_dir / self.MASTER_STATE_FILE
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(asdict(self._master_state), f, indent=2)

    async def _update_progress_file(self) -> None:
        """Update human-readable progress file."""
        features = await self.get_features()
        state = await self.get_execution_state()
        master = self._master_state or MasterState()

        content = f"""=== AUTONOMOUS CODING SESSION ===
Project: {master.project_id or 'unnamed'}
Started: {state.started_at or 'N/A'}
Sessions: {master.sessions_used}

=== PROGRESS ===
[{features.completed}/{features.total}] {round(features.completed/features.total*100, 1) if features.total > 0 else 0}% complete

=== CURRENT FEATURE ===
{state.current_feature or 'None'}

=== STATUS ===
Status: {state.status}
Iteration: {state.iteration}
Cost: ${state.estimated_cost:.2f}

=== LAST UPDATED ===
{datetime.utcnow().isoformat()}Z
"""

        with open(self.project_dir / self.PROGRESS_FILE, 'w') as f:
            f.write(content)
