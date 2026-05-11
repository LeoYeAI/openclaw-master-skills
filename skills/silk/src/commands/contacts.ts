import { addContact, removeContact, getContact, listContacts } from '../contacts.js';
import { outputSuccess } from '../output.js';
import { SdkError } from '../errors.js';

export async function contactsAdd(name: string, address: string) {
  addContact(name, address);
  outputSuccess({ action: 'contact_added', name: name.toLowerCase(), address });
}

export async function contactsRemove(name: string) {
  removeContact(name);
  outputSuccess({ action: 'contact_removed', name: name.toLowerCase() });
}

export async function contactsList() {
  const contacts = listContacts();
  outputSuccess({ action: 'contacts_list', contacts });
}

export async function contactsGet(name: string) {
  const contact = getContact(name);
  if (!contact) {
    throw new SdkError('CONTACT_NOT_FOUND', `Contact "${name.toLowerCase()}" not found`);
  }
  outputSuccess({ action: 'contact_get', name: contact.name, address: contact.address });
}
