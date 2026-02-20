import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Header } from '../components/layout/Header';
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

const ROLES = ['member', 'leader', 'admin'] as const;

const dateFormatter = new Intl.DateTimeFormat('id-ID', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
});

export const AccountsPage = () => {
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
      toast.success('Akun berhasil dibuat');
      setShowCreateDialog(false);
      setCreateEmail('');
      setCreatePassword('');
      setCreateRole('member');
    } catch {
      toast.error('Gagal membuat akun');
    }
  };

  const handleRoleChange = async (userId: number, role: string) => {
    try {
      await updateRole.mutateAsync({
        userId,
        role: role as (typeof ROLES)[number],
      });
      toast.success('Peran berhasil diubah');
    } catch {
      toast.error('Gagal mengubah peran');
    }
  };

  const handleResetPassword = async () => {
    if (!resetTarget) return;
    try {
      await resetPassword.mutateAsync({
        userId: resetTarget.id,
        password: newPassword,
      });
      toast.success('Password berhasil direset');
      setResetTarget(null);
      setNewPassword('');
    } catch {
      toast.error('Gagal mereset password');
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteAccount.mutateAsync(deleteTarget.id);
      toast.success('Akun berhasil dihapus');
      setDeleteTarget(null);
    } catch {
      toast.error('Gagal menghapus akun');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-muted">
        <Header />
        <main id="main-content" className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted-foreground/10 rounded w-1/3" />
            <div className="h-64 bg-muted-foreground/10 rounded" />
          </div>
        </main>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="min-h-screen bg-muted">
        <Header />
        <main id="main-content" className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <p className="text-destructive mb-4">Gagal memuat data akun.</p>
            <Button onClick={() => refetch()}>Coba Lagi</Button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-muted">
      <Header />
      <main id="main-content" className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold tracking-tight">Manajemen Akun</h2>
          <Button onClick={() => setShowCreateDialog(true)}>Buat Akun</Button>
        </div>

        <div className="rounded-md border bg-background">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Email</TableHead>
                <TableHead className="w-40">Peran</TableHead>
                <TableHead>Login Terakhir</TableHead>
                <TableHead className="w-40">Aksi</TableHead>
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
                        <SelectTrigger className="h-8 w-32" aria-label={`Peran ${account.email}`}>
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
                          Reset PW
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          disabled={isSelf}
                          onClick={() => setDeleteTarget(account)}
                        >
                          Hapus
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </main>

      {/* Create Account Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Buat Akun Baru</DialogTitle>
            <DialogDescription>
              Masukkan email, password, dan peran untuk akun baru.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Input
              type="email"
              placeholder="Email"
              value={createEmail}
              onChange={(e) => setCreateEmail(e.target.value)}
              aria-label="Email"
            />
            <Input
              type="password"
              placeholder="Password (min. 6 karakter)"
              value={createPassword}
              onChange={(e) => setCreatePassword(e.target.value)}
              aria-label="Password"
            />
            <Select
              value={createRole}
              onValueChange={(v) => setCreateRole(v as (typeof ROLES)[number])}
            >
              <SelectTrigger aria-label="Peran">
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
              Batal
            </Button>
            <Button
              onClick={handleCreate}
              disabled={!createEmail || createPassword.length < 6 || createAccount.isPending}
            >
              {createAccount.isPending && <Loader2 className="mr-2 size-4 animate-spin" />}
              Buat
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reset Password Dialog */}
      <Dialog open={!!resetTarget} onOpenChange={(open) => !open && setResetTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reset Password</DialogTitle>
            <DialogDescription>
              Masukkan password baru untuk {resetTarget?.email}.
            </DialogDescription>
          </DialogHeader>
          <Input
            type="password"
            placeholder="Password baru (min. 6 karakter)"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            aria-label="Password baru"
          />
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setResetTarget(null)}
              disabled={resetPassword.isPending}
            >
              Batal
            </Button>
            <Button
              onClick={handleResetPassword}
              disabled={newPassword.length < 6 || resetPassword.isPending}
            >
              {resetPassword.isPending && <Loader2 className="mr-2 size-4 animate-spin" />}
              Reset
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Hapus Akun</DialogTitle>
            <DialogDescription>
              Apakah Anda yakin ingin menghapus akun <strong>{deleteTarget?.email}</strong>?
              Tindakan ini tidak dapat dibatalkan. Data evaluasi akan tetap tersimpan.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteTarget(null)}
              disabled={deleteAccount.isPending}
            >
              Batal
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteAccount.isPending}
            >
              {deleteAccount.isPending && <Loader2 className="mr-2 size-4 animate-spin" />}
              Hapus
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
