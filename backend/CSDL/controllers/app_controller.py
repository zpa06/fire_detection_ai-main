"""AppController for FireEyes MVC architecture as defined in the system design."""
from datetime import datetime, timezone
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from backend.CSDL.models.database import FireEyesDB


class AppController:
    """Controller layer coordinating between UI (MainView) and Database (FireEyesDB)."""

    def __init__(self, db_path: Optional[Path | str] = None):
        if db_path is None:
            self._db_path = Path(__file__).resolve().parents[2] / "data" / "fireeyes.db"
        else:
            self._db_path = Path(db_path)
        self._model = FireEyesDB(self._db_path)
        self._model.initialize()

    @property
    def database_path(self) -> Path:
        """Path to SQLite database file."""
        return self._db_path

    @property
    def model(self) -> FireEyesDB:
        """Direct reference to FireEyesDB model."""
        return self._model

    def get_stats(self) -> Dict[str, int]:
        """Thống kê số lượng bản ghi của tất cả 11 bảng trong CSDL."""
        return self._model.counts()

    def get_incidents(
        self,
        acknowledged: Optional[bool] = None,
        limit: Optional[int] = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Lấy danh sách các sự kiện cảnh báo (incidents/alerts)."""
        return self._model.list_incidents(
            acknowledged=acknowledged,
            limit=limit,
            offset=offset
        )

    def run_demo(self) -> Dict[str, Any]:
        """Tạo dữ liệu giả lập (seed demo, frame, detection, incident, notification).

        Tương ứng với nút 'Tạo demo' trong Class Diagram MVC.
        """
        ids = self._model.seed_demo()

        now_utc = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        req_suffix = int(time.time() * 1000)

        # Hộp bounding box giả lập lớp Khói (class_id=0) hoặc Lửa (class_id=1)
        synthetic_box = {
            "class_id": 0,
            "confidence": 0.88,
            "xc": 0.50,
            "yc": 0.45,
            "w": 0.22,
            "h": 0.32,
        }

        frame_id = self._model.record_frame(
            camera_id=ids["camera_id"],
            model_id=ids["model_id"],
            request_id=f"demo-frame-{req_suffix}",
            captured_at=now_utc,
            detections=[synthetic_box],
        )

        detections = self._model.frame_detections(frame_id)
        detection_id = detections[0]["id"]

        incident_id = self._model.open_incident(
            detection_id=detection_id,
            rule_description="MANUAL DEMO: AI confirmed smoke across multiple frames (synthetic)",
        )

        notification_id = self._model.simulate_notification(
            incident_id=incident_id,
            contact_id=ids["contact_id"],
        )

        return {
            "message": (
                "DEMO CSDL: Dữ liệu giả lập đã được tạo thành công vào CSDL. "
                "Bao gồm Frame, Detection, Incident và Simulated Notification."
            ),
            "frame_id": frame_id,
            "detection_id": detection_id,
            "incident_id": incident_id,
            "notification_id": notification_id,
            "stats": self.get_stats(),
            "incidents": self.get_incidents(limit=10),
        }

    # ─── Locations & Cameras Operations ───
    def get_locations(self) -> List[Dict[str, Any]]:
        """Lấy danh sách các địa điểm giám sát."""
        return self._model.list_locations()

    def get_location(self, location_id: int) -> Optional[Dict[str, Any]]:
        """Lấy thông tin một địa điểm theo ID."""
        return self._model.get_location(location_id)

    def create_location(self, name: str, address: str) -> int:
        """Tạo địa điểm mới."""
        return self._model.create_location(name.strip(), address.strip())

    def get_cameras(self) -> List[Dict[str, Any]]:
        """Lấy danh sách tất cả camera trong hệ thống."""
        return self._model.list_cameras()

    def get_camera(self, camera_id: int) -> Optional[Dict[str, Any]]:
        """Lấy thông tin một camera theo ID."""
        return self._model.get_camera(camera_id)

    def create_camera(self, location_id: int, name: str, source_ref: str) -> int:
        """Đăng ký camera mới vào một địa điểm."""
        return self._model.create_camera(location_id, name.strip(), source_ref.strip())

    def get_camera_status(self, camera_id: int) -> Optional[Dict[str, Any]]:
        """Lấy trạng thái kết nối và hoạt động của camera."""
        return self._model.get_camera_status(camera_id)

    def set_camera_enabled(self, camera_id: int, enabled: bool) -> Dict[str, Any]:
        """Bật hoặc tắt trạng thái camera."""
        return self._model.set_camera_enabled(camera_id, enabled)

    def record_camera_heartbeat(self, camera_id: int) -> Dict[str, Any]:
        """Cập nhật tín hiệu sống (heartbeat) cho camera."""
        return self._model.record_camera_heartbeat(camera_id)

    # ─── Contacts & Notifications ───
    def get_contacts(self, location_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Lấy danh sách người nhận thông báo khẩn cấp."""
        return self._model.list_contacts(location_id=location_id)

    def get_contact(self, contact_id: int) -> Optional[Dict[str, Any]]:
        """Lấy thông tin người nhận theo ID."""
        return self._model.get_contact(contact_id)

    def create_contact(
        self,
        location_id: int,
        name: str,
        destination: str,
        channel: str
    ) -> int:
        """Thêm người nhận cảnh báo mới."""
        return self._model.create_contact(location_id, name, destination, channel)

    def get_notifications(
        self,
        incident_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Lấy danh sách thông báo đã gửi/giả lập."""
        return self._model.list_notifications(incident_id=incident_id)

    # ─── Incidents & Lifecycle Operations ───
    def get_incident(self, incident_id: int) -> Optional[Dict[str, Any]]:
        """Lấy chi tiết sự cố theo ID."""
        return self._model.get_incident(incident_id)

    def acknowledge_incident(self, incident_id: int, acknowledged_by: str) -> Dict[str, Any]:
        """Cán bộ trực ban xác nhận đã xem cảnh báo."""
        return self._model.acknowledge_incident(incident_id, acknowledged_by.strip())

    def close_incident(self, incident_id: int, status: str, note: str) -> Dict[str, Any]:
        """Xử lý và đóng sự kiện (resolved hoặc false_alarm)."""
        return self._model.close_incident(incident_id, status, note.strip())

    # ─── Datasets & Models ───
    def get_datasets(self) -> List[Dict[str, Any]]:
        """Lấy danh sách các phiên bản dataset huấn luyện."""
        return self._model.list_datasets()

    def get_dataset(self, dataset_id: int) -> Optional[Dict[str, Any]]:
        """Lấy thông tin phiên bản dataset theo ID."""
        return self._model.get_dataset(dataset_id)

    def get_models(self) -> List[Dict[str, Any]]:
        """Lấy danh sách các phiên bản mô hình AI."""
        return self._model.list_models()

    def get_model(self, model_id: int) -> Optional[Dict[str, Any]]:
        """Lấy thông tin phiên bản mô hình theo ID."""
        return self._model.get_model(model_id)

    # ─── Detections & History ───
    def get_detection_history(
        self,
        camera_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Lấy lịch sử nhận diện khung hình từ CSDL."""
        return self._model.list_detection_history(camera_id=camera_id, limit=limit, offset=offset)

    def record_frame(
        self,
        camera_id: int,
        model_id: int,
        request_id: str,
        captured_at: str,
        detections: List[Dict[str, Any]],
        snapshot_path: Optional[str] = None,
    ) -> int:
        """Ghi nhận một khung hình kèm các hộp nhận diện AI vào CSDL."""
        return self._model.record_frame(
            camera_id=camera_id,
            model_id=model_id,
            request_id=request_id,
            captured_at=captured_at,
            detections=detections,
            snapshot_path=snapshot_path,
        )

