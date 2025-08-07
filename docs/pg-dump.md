Here's how to resolve this issue step-by-step:

---

### 1. **Use the Same PostgreSQL Version for Restore**

To restore the dump file properly, you need to use the same PostgreSQL version as the one used to create the dump file. In this case, install PostgreSQL 14 temporarily and use its `pg_restore` utility to restore the dump into a PostgreSQL 16 database.

#### Steps:

- **Install PostgreSQL 14** alongside PostgreSQL 16 (or use a container if you're concerned about conflicts).
- Use the `pg_restore` from PostgreSQL 14 to restore the database:

  ```bash
  /path/to/postgresql14/bin/pg_restore -d dbname selective_backup.bak
  ```

Once restored, you can then use `pg_dump` from PostgreSQL 16 to back it up again and move forward with using version 16.

---

### 2. **Use a Plain SQL Dump Instead**

If you still have access to the original PostgreSQL 14 server, you can re-export the database as a **plain SQL script** instead of a custom-format dump. The plain format is text-based and does not rely on `pg_restore`:

#### Re-export as a plain SQL dump:

```bash
pg_dump -Fp dbname > selective_backup.sql
```

#### Restore using `psql`:

```bash
psql -d dbname -f selective_backup.sql
```

The plain SQL format is more portable and should work across PostgreSQL versions (with some limitations if there are breaking changes in syntax).

---

### 3. **Upgrade the Dump File Using Intermediate Steps**

If you cannot access the original PostgreSQL 14 server or cannot install PostgreSQL 14 on your system, you can upgrade the dump file by restoring it into a PostgreSQL 14 database and then exporting it again with `pg_dump` from PostgreSQL 16.

#### Use Docker as an alternative:

You can spin up a Docker container running PostgreSQL 14 to handle this step. For example:

```bash
docker run -d --name pg14 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:14
```

Restore the dump file using PostgreSQL 14’s `pg_restore` inside the container, then export it again using PostgreSQL 16.

---

### 4. **Key Takeaways**

- PostgreSQL custom-format dumps (`-Fc`) are **not guaranteed to be forward-compatible**. Always use the same or higher version of `pg_restore` compared to the `pg_dump` version.
- Use a **plain SQL format** (`-Fp`) for maximum portability if you need to move data between major versions without intermediate installations.
- Consider using Docker or containers to manage PostgreSQL version dependencies more easily when migrating databases.

Let me know if you'd like help with the specific commands for Docker or installation! 🔨🤖
