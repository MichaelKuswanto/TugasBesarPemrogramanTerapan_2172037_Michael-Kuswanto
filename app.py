from flask import Flask, jsonify, request, render_template
from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, declarative_base
from sqlalchemy.exc import IntegrityError
import datetime

Base = declarative_base()

class Penduduk(Base):
    __tablename__ = 'penduduk'

    id_penduduk = Column(Integer, primary_key=True, nullable=False)
    nama = Column(String(100), nullable=False)
    alamat = Column(String(200), nullable=False)
    pengajuan_sertifikat = relationship('PengajuanSertifikat', backref='penduduk')

    def json(self):
        return {'id_penduduk': self.id_penduduk, 'nama': self.nama, 'alamat': self.alamat}

class PengajuanSertifikat(Base):
    __tablename__ = 'pengajuan_sertifikat'

    id_pengajuan = Column(Integer, primary_key=True, nullable=False)
    jenis_sertifikat = Column(String(100), nullable=False)
    tanggal_pengajuan = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    penduduk_id = Column(Integer, ForeignKey('penduduk.id_penduduk'), nullable=False)
    sertifikat = relationship('Sertifikat', backref='pengajuan_sertifikat')

    def json(self):
        return {
            'id_pengajuan': self.id_pengajuan,
            'jenis_sertifikat': self.jenis_sertifikat,
            'tanggal_pengajuan': self.tanggal_pengajuan,
            'penduduk_id': self.penduduk_id
        }

class Sertifikat(Base):
    __tablename__ = 'sertifikat'

    id_sertifikat = Column(Integer, primary_key=True, nullable=False)
    nomor_sertifikat = Column(String(100), nullable=False)
    tanggal_terbit = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    pengajuan_sertifikat_id = Column(Integer, ForeignKey('pengajuan_sertifikat.id_pengajuan'), nullable=False)

    def json(self):
        return {
            'id_sertifikat': self.id_sertifikat,
            'nomor_sertifikat': self.nomor_sertifikat,
            'tanggal_terbit': self.tanggal_terbit,
            'pengajuan_sertifikat_id': self.pengajuan_sertifikat_id
        }

app = Flask(__name__)

engine = create_engine('sqlite:///certificate.db')
Base.metadata.create_all(engine)
session = Session(engine)

@app.route('/')
def index():
    with Session(engine) as session:
        penduduk = session.query(Penduduk).all()
        pengajuan_sertifikat = session.query(PengajuanSertifikat).all()
        sertifikat = session.query(Sertifikat).all()
        session.close()
        return render_template('index.html', penduduk=penduduk, pengajuan_sertifikat=pengajuan_sertifikat, sertifikat=sertifikat)

@app.route('/penduduk', methods=['GET', 'POST'])
def handle_penduduk():
    with Session(engine) as session:
        if request.method == 'GET':
            penduduk = session.query(Penduduk).all()
            return render_template('penduduk.html', penduduk=penduduk)

        if request.method == 'POST':
            data = request.get_json()
            if not data or not data.get('nama') or not data.get('alamat'):
                return jsonify({'message': 'Masukkan nama dan alamat'}), 400

            new_penduduk = Penduduk(nama=data['nama'], alamat=data['alamat'])
            try:
                session.add(new_penduduk)
                session.commit()
                return jsonify(new_penduduk.json()), 201
            except IntegrityError:
                return jsonify({'message': 'Gagal menambahkan penduduk'}), 500
            finally:
                session.close()

@app.route('/pengajuan_sertifikat', methods=['GET', 'POST'])
def handle_pengajuan_sertifikat():
    with Session(engine) as session:
        if request.method == 'GET':
            pengajuan_sertifikat = session.query(PengajuanSertifikat).all()
            return render_template('pengajuan.html', pengajuan_sertifikat=pengajuan_sertifikat)

        if request.method == 'POST':
            data = request.get_json()
            if not data or not data.get('jenis_sertifikat') or not data.get('penduduk_id'):
                return jsonify({'message': 'Masukkan jenis sertifikat dan ID penduduk'}), 400

            new_pengajuan = PengajuanSertifikat(jenis_sertifikat=data['jenis_sertifikat'], penduduk_id=data['penduduk_id'])
            try:
                session.add(new_pengajuan)
                session.commit()
                return jsonify(new_pengajuan.json()), 201
            except IntegrityError:
                return jsonify({'message': 'Gagal menambahkan pengajuan sertifikat'}), 500
            finally:
                session.close()

@app.route('/sertifikat', methods=['GET', 'POST'])
def handle_sertifikat():
    with Session(engine) as session:
        if request.method == 'GET':
            sertifikat = session.query(Sertifikat).all()
            return render_template('sertifikat.html', sertifikat=sertifikat)

        if request.method == 'POST':
            data = request.get_json()
            if not data or not data.get('nomor_sertifikat') or not data.get('pengajuan_sertifikat_id'):
                return jsonify({'message': 'Masukkan nomor sertifikat dan ID pengajuan sertifikat'}), 400

            new_sertifikat = Sertifikat(nomor_sertifikat=data['nomor_sertifikat'], pengajuan_sertifikat_id=data['pengajuan_sertifikat_id'])
            try:
                session.add(new_sertifikat)
                session.commit()
                return jsonify(new_sertifikat.json()), 201
            except IntegrityError:
                return jsonify({'message': 'Gagal menambahkan sertifikat'}), 500
            finally:
                session.close()

@app.route('/penduduk/<int:id_penduduk>', methods=['GET'])
def get_penduduk(id_penduduk):
    with Session(engine) as session:
        penduduk = session.query(Penduduk).filter_by(id_penduduk=id_penduduk).first()
        if penduduk:
            return jsonify(penduduk.json())
        else:
            return jsonify({'message': 'Penduduk tidak ditemukan'}), 404

@app.route('/pengajuan_sertifikat/<int:id_pengajuan>', methods=['GET'])
def get_pengajuan(id_pengajuan):
    with Session(engine) as session:
        pengajuan = session.query(PengajuanSertifikat).filter_by(id_pengajuan=id_pengajuan).first()
        if pengajuan:
            return jsonify(pengajuan.json())
        else:
            return jsonify({'message': 'pengajuan tidak ditemukan'}), 404

@app.route('/sertifikat/<int:id_sertifikat>', methods=['GET'])
def get_sertifikat(id_sertifikat):
    with Session(engine) as session:
        sertifikat = session.query(Sertifikat).filter_by(id_sertifikat=id_sertifikat).first()
        if sertifikat:
            return jsonify(sertifikat.json())
        else:
            return jsonify({'message': 'sertifikat tidak ditemukan'}), 404

@app.route('/penduduk/<int:id_penduduk>', methods=['PUT'])
def update_penduduk(id_penduduk):
    with Session(engine) as session:
        penduduk = session.query(Penduduk).get(id_penduduk)
        if not penduduk:
            session.close()
            return jsonify({'message': 'Penduduk tidak ditemukan'}), 404

        data = request.get_json()
        if not data:
            session.close()
            return jsonify({'message': 'Data tidak ditemukan'}), 400

        if 'nama' in data:
            penduduk.nama = data['nama']
        if 'alamat' in data:
            penduduk.alamat = data['alamat']

        try:
            session.commit()
            session.close()
            return jsonify(penduduk.json()), 200
        except IntegrityError:
            session.rollback()
            session.close()
            return jsonify({'message': 'Gagal mengupdate penduduk'}), 500

# Rute untuk menghapus Penduduk
@app.route('/penduduk/<int:id_penduduk>', methods=['DELETE'])
def delete_penduduk(id_penduduk):
    with Session(engine) as session:
        penduduk = session.query(Penduduk).get(id_penduduk)
        if not penduduk:
            session.close()
            return jsonify({'message': 'Penduduk tidak ditemukan'}), 404

        try:
            session.delete(penduduk)
            session.commit()
            session.close()
            return jsonify({'message': 'Penduduk berhasil dihapus'}), 200
        except IntegrityError:
            session.rollback()
            session.close()
            return jsonify({'message': 'Gagal menghapus penduduk'}), 500

@app.route('/pengajuan_sertifikat/<int:id_pengajuan>', methods=['PUT'])
def update_pengajuan_sertifikat(id_pengajuan):
    with Session(engine) as session:
        pengajuan = session.query(PengajuanSertifikat).get(id_pengajuan)
        if not pengajuan:
            session.close()
            return jsonify({'message': 'Pengajuan sertifikat tidak ditemukan'}), 404

        data = request.get_json()
        if not data:
            session.close()
            return jsonify({'message': 'Data tidak ditemukan'}), 400

        if 'jenis_sertifikat' in data:
            pengajuan.jenis_sertifikat = data['jenis_sertifikat']
        if 'penduduk_id' in data:
            pengajuan.penduduk_id = data['penduduk_id']

        try:
            session.commit()
            session.close()
            return jsonify(pengajuan.json()), 200
        except IntegrityError:
            session.rollback()
            session.close()
            return jsonify({'message': 'Gagal mengupdate pengajuan sertifikat'}), 500

@app.route('/pengajuan_sertifikat/<int:id_pengajuan>', methods=['DELETE'])
def delete_pengajuan_sertifikat(id_pengajuan):
    with Session(engine) as session:
        pengajuan = session.query(PengajuanSertifikat).get(id_pengajuan)
        if not pengajuan:
            session.close()
            return jsonify({'message': 'Pengajuan sertifikat tidak ditemukan'}), 404

        try:
            session.delete(pengajuan)
            session.commit()
            session.close()
            return jsonify({'message': 'Pengajuan sertifikat berhasil dihapus'}), 200
        except IntegrityError:
            session.rollback()
            session.close()
            return jsonify({'message': 'Gagal menghapus pengajuan sertifikat'}), 500

@app.route('/sertifikat/<int:id_sertifikat>', methods=['PUT'])
def update_sertifikat(id_sertifikat):
    with Session(engine) as session:
        sertifikat = session.query(Sertifikat).get(id_sertifikat)
        if not sertifikat:
            session.close()
            return jsonify({'message': 'Sertifikat tidak ditemukan'}), 404

        data = request.get_json()
        if not data:
            session.close()
            return jsonify({'message': 'Data tidak ditemukan'}), 400

        if 'nomor_sertifikat' in data:
            sertifikat.nomor_sertifikat = data['nomor_sertifikat']
        if 'pengajuan_sertifikat_id' in data:
            sertifikat.pengajuan_sertifikat_id = data['pengajuan_sertifikat_id']

        try:
            session.commit()
            session.close()
            return jsonify(sertifikat.json()), 200
        except IntegrityError:
            session.rollback()
            session.close()
            return jsonify({'message': 'Gagal mengupdate sertifikat'}), 500


@app.route('/sertifikat/<int:id_sertifikat>', methods=['DELETE'])
def delete_sertifikat(id_sertifikat):
    with Session(engine) as session:
        sertifikat = session.query(Sertifikat).get(id_sertifikat)
        if not sertifikat:
            session.close()
            return jsonify({'message': 'Sertifikat tidak ditemukan'}), 404

        try:
            session.delete(sertifikat)
            session.commit()
            session.close()
            return jsonify({'message': 'Sertifikat berhasil dihapus'}), 200
        except IntegrityError:
            session.rollback()
            session.close()
            return jsonify({'message': 'Gagal menghapus sertifikat'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8090)