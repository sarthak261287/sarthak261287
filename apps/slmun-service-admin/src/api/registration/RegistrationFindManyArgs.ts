import { RegistrationWhereInput } from "./RegistrationWhereInput";
import { RegistrationOrderByInput } from "./RegistrationOrderByInput";

export type RegistrationFindManyArgs = {
  where?: RegistrationWhereInput;
  orderBy?: Array<RegistrationOrderByInput>;
  skip?: number;
  take?: number;
};
