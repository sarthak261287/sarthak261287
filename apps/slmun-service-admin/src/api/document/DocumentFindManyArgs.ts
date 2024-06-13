import { DocumentWhereInput } from "./DocumentWhereInput";
import { DocumentOrderByInput } from "./DocumentOrderByInput";

export type DocumentFindManyArgs = {
  where?: DocumentWhereInput;
  orderBy?: Array<DocumentOrderByInput>;
  skip?: number;
  take?: number;
};
