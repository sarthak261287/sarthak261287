import { RegistrationUpdateManyWithoutUsersInput } from "./RegistrationUpdateManyWithoutUsersInput";
import { InputJsonValue } from "../../types";

export type UserUpdateInput = {
  email?: string | null;
  firstName?: string | null;
  lastName?: string | null;
  password?: string;
  registrations?: RegistrationUpdateManyWithoutUsersInput;
  roles?: InputJsonValue;
  username?: string;
};
