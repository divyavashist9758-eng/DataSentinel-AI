from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

class DatasetSchemaOut(BaseModel):
    id: int
    column_name: str
    data_type: str
    is_nullable: bool
    unique_count: int
    sample_values: Optional[List[Any]] = None

    class Config:
        from_attributes = True

class DatasetVersionOut(BaseModel):
    id: int
    dataset_id: int
    version_num: int
    file_path: str
    row_count: int
    column_count: int
    change_summary: Optional[str] = None
    is_remediated: bool
    created_at: datetime
    schemas: List[DatasetSchemaOut] = []

    class Config:
        from_attributes = True

class DatasetOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    file_type: str
    original_filename: str
    file_size_bytes: int
    row_count: int
    column_count: int
    sha256_hash: str
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    latest_quality_score: Optional[float] = None
    versions_count: Optional[int] = None

    class Config:
        from_attributes = True

class DatasetDetailOut(DatasetOut):
    versions: List[DatasetVersionOut] = []
    sample_rows: Optional[List[Dict[str, Any]]] = None

class DatabaseConnectionConfig(BaseModel):
    name: str
    description: Optional[str] = None
    connection_url: str
    query_or_table: str

