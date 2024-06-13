import { RegistrationCreateNestedManyWithoutUsersInput } from "./RegistrationCreateNestedManyWithoutUsersInput";
import { InputJsonValue } from "../../types";

export type UserCreateInput = {
  email?: string | null;
  firstName?: string | null;
  lastName?: string | null;
  password: string;
  registrations?: RegistrationCreateNestedManyWithoutUsersInput;
  roles: InputJsonValue;
  username: string;
};
