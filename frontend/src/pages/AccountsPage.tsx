import { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { useCurrentUser } from '../hooks/useCurrentUser';
import {
  useAccounts,
  useCreateAccount,
  useUpdateRole,
  useResetPassword,
  useDeleteAccount,
  type Account,
} from '../hooks/useAccounts';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import { getIntlLocale } from '../lib/languages';

const ROLES = ['member', 'leader', 'admin'] as const;

export const AccountsPage = () => {
  const { t, i18n } = useTranslation();
  const dateFormatter = useMemo(
    () => new Intl.DateTimeFormat(getIntlLocale(i18n.language), {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }),
    [i18n.language],
  );
  const { profile } = useCurrentUser();
  const { accounts, isLoading, isError, refetch } = useAccounts();
  const createAccount = useCreateAccount();
  const updateRole = useUpdateRole();
  const resetPassword = useResetPassword();
  const deleteAccount = useDeleteAccount();

  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [resetTarget, setResetTarget] = useState<Account | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Account | null>(null);

  // Create form state
  const [createEmail, setCreateEmail] = useState('');
  const [createPassword, setCreatePassword] = useState('');
  const [createRole, setCreateRole] = useState<(typeof ROLES)[number]>('member');

  // Reset password state
  const [newPassword, setNewPassword] = useState('');

  const handleCreate = async () => {
    try {
      await createAccount.mutateAsync({
        email: createEmail,
        password: createPassword,
        role: createRole,
      });
      toast.success(t('accounts.toast.createSuccess'));
      setShowCreateDialog(false);
      setCreateEmail('');
      setCreatePassword('');
      setCreateRole('member');
    } catch {
      toast.error(t('accounts.toast.createError'));
    }
  };

  const handleRoleChange = async (userId: number, role: string) => {
    try {
      await updateRole.mutateAsync({
        userId,
        role: role as (typeof ROLES)[number],
      });
      toast.success(t('accounts.toast.roleChangeSuccess'));
    } catch {
      toast.error(t('accounts.toast.roleChangeError'));
    }
  };

  const handleResetPassword = async () => {
    if (!resetTarget) return;
    try {
      await resetPassword.mutateAsync({
        userId: resetTarget.id,
        password: newPassword,
      });
      toast.success(t('accounts.toast.resetSuccess'));
      setResetTarget(null);
      setNewPassword('');
    } catch {
      toast.error(t('accounts.toast.resetError'));
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteAccount.mutateAsync(deleteTarget.id);
      toast.success(t('accounts.toast.deleteSuccess'));
      setDeleteTarget(null);
    } catch {
      toast.error(t('accounts.toast.deleteError'));
    }
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted-foreground/10 rounded w-1/3" />
          <div className="h-64 bg-muted-foreground/10 rounded" />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="text-center py-12">
          <p className="text-destructive mb-4">{t('accounts.errorLoading')}</p>
          <Button onClick={() => refetch()}>{t('common.retry')}</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold tracking-tight">{t('accounts.title')}</h2>
        <Button onClick={() => setShowCreateDialog(true)}>{t('accounts.createAccount')}</Button>
      </div>

      <div className="rounded-md border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t('accounts.email')}</TableHead>
              <TableHead className="w-40">{t('accounts.role')}</TableHead>
              <TableHead>{t('accounts.lastLogin')}</TableHead>
              <TableHead className="w-40">{t('accounts.actions')}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {accounts.map((account) => {
              const isSelf = account.id === Number(profile?.id);
              return (
                <TableRow key={account.id}>
                  <TableCell className="font-medium">{account.email}</TableCell>
                  <TableCell>
                    <Select
                      value={account.role}
                      onValueChange={(value) => handleRoleChange(account.id, value)}
                      disabled={isSelf}
                    >
                      <SelectTrigger className="h-8 w-32" aria-label={t('accounts.roleFor', { email: account.email })}>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {ROLES.map((role) => (
                          <SelectItem key={role} value={role}>
                            {role}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </TableCell>
                  <TableCell className="text-muted-foreground text-sm">
                    {account.last_login
                      ? dateFormatter.format(new Date(account.last_login))
                      : '—'}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={isSelf}
                        onClick={() => {
                          setResetTarget(account);
                          setNewPassword('');
                        }}
                      >
                        {t('accounts.resetPw')}
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        disabled={isSelf}
                        onClick={() => setDeleteTarget(account)}
                      >
                        {t('accounts.delete')}
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {/* Create Account Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('accounts.dialog.createTitle')}</DialogTitle>
            <DialogDescription>
              {t('accounts.dialog.createDescription')}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Input
              type="email"
              placeholder={t('accounts.email')}
              value={createEmail}
              onChange={(e) => setCreateEmail(e.target.value)}
              aria-label={t('accounts.email')}
            />
            <Input
              type="password"
              placeholder={t('accounts.dialog.passwordPlaceholder')}
              value={createPassword}
              onChange={(e) => setCreatePassword(e.target.value)}
              aria-label={t('accounts.dialog.password')}
            />
            <Select
              value={createRole}
              onValueChange={(v) => setCreateRole(v as (typeof ROLES)[number])}
            >
              <SelectTrigger aria-label={t('accounts.role')}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ROLES.map((role) => (
                  <SelectItem key={role} value={role}>
                    {role}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowCreateDialog(false)}
              disabled={createAccount.isPending}
            >
              {t('common.cancel')}
            </Button>
            <Button
              onClick={handleCreate}
              disabled={!createEmail || createPassword.length < 6 || createAccount.isPending}
            >
              {createAccount.isPending && <Loader2 className="mr-2 size-4 animate-spin" />}
              {t('accounts.dialog.create')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reset Password Dialog */}
      <Dialog open={!!resetTarget} onOpenChange={(open) => !open && setResetTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('accounts.dialog.resetTitle')}</DialogTitle>
            <DialogDescription>
              {t('accounts.dialog.resetDescription', { email: resetTarget?.email })}
            </DialogDescription>
          </DialogHeader>
          <Input
            type="password"
            placeholder={t('accounts.dialog.newPasswordPlaceholder')}
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            aria-label={t('accounts.dialog.newPassword')}
          />
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setResetTarget(null)}
              disabled={resetPassword.isPending}
            >
              {t('common.cancel')}
            </Button>
            <Button
              onClick={handleResetPassword}
              disabled={newPassword.length < 6 || resetPassword.isPending}
            >
              {resetPassword.isPending && <Loader2 className="mr-2 size-4 animate-spin" />}
              {t('accounts.dialog.reset')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('accounts.dialog.deleteTitle')}</DialogTitle>
            <DialogDescription>
              {t('accounts.dialog.deleteDescription', { email: deleteTarget?.email })}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteTarget(null)}
              disabled={deleteAccount.isPending}
            >
              {t('common.cancel')}
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteAccount.isPending}
            >
              {deleteAccount.isPending && <Loader2 className="mr-2 size-4 animate-spin" />}
              {t('accounts.delete')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
