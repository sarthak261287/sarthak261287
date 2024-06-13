import { Document as TDocument } from "../api/document/Document";

export const DOCUMENT_TITLE_FIELD = "name";

export const DocumentTitle = (record: TDocument): string => {
  return record.name?.toString() || String(record.id);
};
